import time
import csv
import random
import json
from pathlib import Path
from scraper import WebScraper
import datetime
import argparse
import sys


def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description="Scrape NeurIPS papers with checkpoint support"
    )
    parser.add_argument(
        "--resume", action="store_true", help="Resume from last checkpoint"
    )
    parser.add_argument(
        "--run-dir", type=str, help="Specify run directory to resume from"
    )
    parser.add_argument(
        "--max-proceedings",
        type=int,
        default=None,
        help="Maximum number of proceedings to process before stopping",
    )
    args = parser.parse_args()

    # Record start time
    start_time = time.time()

    source_url = "https://papers.nips.cc/"
    scraper = WebScraper(source_url)

    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)

    # Handle resuming from checkpoint
    checkpoint_file = None
    checkpoint_data = {}
    start_proc_idx = 0
    proceedings = []
    all_papers_data = []
    total_paper_count = 0

    if args.resume:
        if args.run_dir:
            run_dir = output_dir / args.run_dir
            if not run_dir.exists():
                print(f"Error: Run directory {run_dir} does not exist")
                sys.exit(1)
        else:
            # Find the most recent run directory
            run_dirs = sorted(
                [
                    d
                    for d in output_dir.iterdir()
                    if d.is_dir() and d.name.startswith("run_")
                ],
                key=lambda x: x.name,
                reverse=True,
            )
            if not run_dirs:
                print("No previous run directories found. Starting a new run.")
                args.resume = False
            else:
                run_dir = run_dirs[0]
                print(f"Resuming from most recent run: {run_dir.name}")

        if args.resume:
            checkpoint_file = run_dir / "checkpoint.json"
            if checkpoint_file.exists():
                with open(checkpoint_file, "r") as f:
                    checkpoint_data = json.load(f)

                proceedings = checkpoint_data.get("proceedings", [])
                start_proc_idx = checkpoint_data.get("next_proc_idx", 0)
                total_paper_count = checkpoint_data.get("total_paper_count", 0)

                # Load previously collected papers
                all_papers_file = run_dir / "all_papers.csv"
                if all_papers_file.exists():
                    all_papers_data = load_from_csv(all_papers_file)

                print(f"Resuming from proceeding {start_proc_idx+1}/{len(proceedings)}")
            else:
                print("No checkpoint file found. Starting a new run.")
                args.resume = False

    # Create a new run if not resuming
    if not args.resume:
        # Create a timestamp for this run
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        run_dir = output_dir / f"run_{timestamp}"
        run_dir.mkdir(exist_ok=True)
        checkpoint_file = run_dir / "checkpoint.json"

        print(
            f"Starting new scraping run at {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )
        print(f"Output directory: {run_dir}")

        # Collect proceedings
        proceedings_start = time.time()
        proceedings = scraper.collect_proceedings()
        proceedings_time = time.time() - proceedings_start
        print(
            f"Collected {len(proceedings)} proceedings in {proceedings_time:.2f} seconds"
        )

        # Save proceedings list
        with open(run_dir / "proceedings.txt", "w") as f:
            for proc in proceedings:
                f.write(f"{proc}\n")

        # Create initial checkpoint
        save_checkpoint(
            checkpoint_file,
            {
                "proceedings": proceedings,
                "next_proc_idx": 0,
                "total_paper_count": 0,
                "last_update": datetime.datetime.now().isoformat(),
            },
        )

    # Determine how many proceedings to process
    remaining_proceedings = proceedings[start_proc_idx:]
    if args.max_proceedings:
        proceedings_to_process = remaining_proceedings[: args.max_proceedings]
        print(
            f"Will process {len(proceedings_to_process)} proceedings (max: {args.max_proceedings})"
        )
    else:
        proceedings_to_process = remaining_proceedings
        print(f"Will process all {len(proceedings_to_process)} remaining proceedings")

    # Collect papers for each proceeding
    for i, proc_url in enumerate(proceedings_to_process):
        proc_idx = start_proc_idx + i
        proc_start = time.time()

        # Extract year from URL for filename
        year = proc_url.split("/")[-1]
        proc_name = f"proceeding_{year}"

        print(f"\nProcessing proceeding {proc_idx+1}/{len(proceedings)}: {proc_url}")

        # Check if this proceeding has already been processed
        proc_file = run_dir / f"{proc_name}.csv"
        if proc_file.exists():
            print(f"Proceeding {year} already processed. Skipping.")
            continue

        # Collect papers for this proceeding
        papers_dict = scraper.collect_papers([proc_url])
        paper_urls = papers_dict[proc_url]

        print(f"Found {len(paper_urls)} papers in proceeding {year}")

        # Create a list to store papers for this proceeding
        proc_papers_data = []

        # Process each paper
        for paper_idx, paper_url in enumerate(paper_urls):
            # Add random delay to avoid overloading the server
            time.sleep(random.uniform(1, 3))

            # Extract paper data
            paper_data = scraper.collect_paper_data(paper_url)
            paper_data["proceeding"] = proc_url
            paper_data["url"] = paper_url
            paper_data["year"] = year

            # Add to both lists
            proc_papers_data.append(paper_data)
            all_papers_data.append(paper_data)

            # Update counters
            total_paper_count += 1

            # Print progress
            if (paper_idx + 1) % 10 == 0:
                elapsed = time.time() - start_time
                papers_per_second = total_paper_count / elapsed
                print(
                    f"Processed {paper_idx+1}/{len(paper_urls)} papers in proceeding {year} "
                    + f"(Total: {total_paper_count}, Rate: {papers_per_second:.2f} papers/sec)"
                )

            # Update checkpoint periodically
            if (paper_idx + 1) % 100 == 0:
                # Update checkpoint
                save_checkpoint(
                    checkpoint_file,
                    {
                        "proceedings": proceedings,
                        "next_proc_idx": proc_idx,
                        "current_proc_paper_idx": paper_idx + 1,
                        "total_paper_count": total_paper_count,
                        "last_update": datetime.datetime.now().isoformat(),
                    },
                )

        # Save all papers for this proceeding
        save_to_csv(proc_papers_data, proc_file)

        # Save all papers collected so far
        save_to_csv(all_papers_data, run_dir / "all_papers.csv")

        # Calculate and print timing for this proceeding
        proc_time = time.time() - proc_start
        print(
            f"Completed proceeding {year}: {len(paper_urls)} papers in {proc_time:.2f} seconds "
            + f"({len(paper_urls)/proc_time:.2f} papers/sec)"
        )

        # Update checkpoint after completing a proceeding
        save_checkpoint(
            checkpoint_file,
            {
                "proceedings": proceedings,
                "next_proc_idx": proc_idx + 1,
                "total_paper_count": total_paper_count,
                "last_update": datetime.datetime.now().isoformat(),
            },
        )

    # Calculate and print total timing
    total_time = time.time() - start_time
    print(
        f"\nScraping complete at {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    )
    print(f"Total time: {total_time:.2f} seconds ({total_time/60:.2f} minutes)")
    print(f"Total papers: {len(all_papers_data)}")
    print(f"Average rate: {len(all_papers_data)/total_time:.2f} papers/second")
    print(f"All data saved to {run_dir}")

    # Final checkpoint update
    if proc_idx + 1 >= len(proceedings):
        print("All proceedings have been processed!")
        # Mark the checkpoint as complete
        save_checkpoint(
            checkpoint_file,
            {
                "proceedings": proceedings,
                "next_proc_idx": len(proceedings),
                "total_paper_count": total_paper_count,
                "completed": True,
                "completion_time": datetime.datetime.now().isoformat(),
            },
        )


def save_to_csv(data, filepath):
    if not data:
        return

    fieldnames = data[0].keys()
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)
    print(f"Data saved to {filepath}")


def load_from_csv(filepath):
    data = []
    with open(filepath, "r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            data.append(row)
    return data


def save_checkpoint(filepath, data):
    with open(filepath, "w") as f:
        json.dump(data, f, indent=2)


if __name__ == "__main__":
    main()
