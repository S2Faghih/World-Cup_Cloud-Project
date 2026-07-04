import os
import sys
import time

def dispatch_live_batches(source_log, output_dir, batch_size=200):
    """
    Monitors the active monolithic Nginx access log and splits new lines
    into separate small JSON Lines batch files to trigger Spark's readStream.
    """
    if not os.path.exists(source_log):
        print(f"[ERROR] Source log file '{source_log}' not found. Please start the traffic generator first.")
        sys.exit(1)
        
    os.makedirs(output_dir, exist_ok=True)
    print(f"[INFO] Ingesting lines from {source_log} into streaming directory {output_dir}...")
    
    with open(source_log, 'r', encoding='utf-8') as f:
        batch_lines = []
        batch_counter = 1
        
        for line in f:
            if line.strip():
                batch_lines.append(line)
            
            # When the window size hits the batch threshold, dump it to the stream directory
            if len(batch_lines) >= batch_size:
                batch_filename = os.path.join(output_dir, f"batch_{str(batch_counter).zfill(4)}.jsonl")
                with open(batch_filename, 'w', encoding='utf-8') as out_f:
                    out_f.writelines(batch_lines)
                
                print(f"[STREAM] Successfully dispatched {batch_filename} with {batch_size} records.")
                batch_lines = []
                batch_counter += 1
                # Simulate realistic real-time streaming interval arrival
                time.sleep(2)
        
        # Dispatch any remaining lines leftover at the end
        if batch_lines:
            batch_filename = os.path.join(output_dir, f"batch_{str(batch_counter).zfill(4)}.jsonl")
            with open(batch_filename, 'w', encoding='utf-8') as out_f:
                out_f.writelines(batch_lines)
            print(f"[STREAM] Dispatched residual batch {batch_filename} with {len(batch_lines)} records.")

if __name__ == "__main__":
    # Paths configured according to the project workspace configuration
    dispatch_live_batches(
        source_log="data/nginx/nginx_access.log",
        output_dir="data/stream/nginx",
        batch_size=200
    )