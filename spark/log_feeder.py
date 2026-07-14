import os
import sys
import time
import argparse

def dispatch_live_batches_continuously(source_log, output_dir, batch_size=200):
    """
    Continuously monitors the Nginx access log. 
    Never shuts down; waits for new lines and streams them to Spark indefinitely.
    """
    if not os.path.exists(source_log):
        print(f"[ERROR] Source log file '{source_log}' not found. Start Nginx/Traffic first.")
        sys.exit(1)
        
    os.makedirs(output_dir, exist_ok=True)
    print(f"[INFO] Continuously tailing {source_log} into {output_dir}... (Press Ctrl+C to stop)")
    
    batch_lines = []
    batch_counter = 1
    
    with open(source_log, 'r', encoding='utf-8') as f:
        while True:
            # Read the next line
            line = f.readline()
            
            # If the line is empty, we reached the end of the file.
            if not line:
                # Wait 1 second for the Traffic Generator to write more data, then try again
                time.sleep(1)
                continue
                
            # If we got a real log line, add it to our current batch
            if line.strip():
                batch_lines.append(line)
            
            # When the batch is full, dispatch it to Spark
            if len(batch_lines) >= batch_size:
                batch_filename = os.path.join(output_dir, f"batch_{str(batch_counter).zfill(4)}.jsonl")
                with open(batch_filename, 'w', encoding='utf-8') as out_f:
                    out_f.writelines(batch_lines)
                
                print(f"[STREAM] Successfully dispatched {batch_filename} with {batch_size} records.")
                batch_lines = []
                batch_counter += 1
                
                # Small sleep to simulate realistic network arrival times
                time.sleep(2)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Live Log Feeder")
    parser.add_argument("--source", type=str, default="data/nginx/nginx_access.log", help="Path to raw monolith log")
    parser.add_argument("--output", type=str, default="data/stream/nginx", help="Path to drop stream batches")
    args = parser.parse_args()

    dispatch_live_batches_continuously(
        source_log=args.source,
        output_dir=args.output,
        batch_size=200
    )