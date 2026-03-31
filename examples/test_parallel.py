import multiprocessing as mp
import time

def worker(conn):
    """Simple worker that waits for a message and responds."""
    print("[Worker] Started and waiting...")
    msg = conn.recv()
    print(f"[Worker] Received: {msg}")

    # Process data
    response = f"Echo: {msg} at {time.time()}"

    # Send back
    conn.send(response)
    print("[Worker] Response sent. Terminating.")
    conn.close()

if __name__ == "__main__":
    # Create the pipe
    parent_conn, child_conn = mp.Pipe()

    # Start the process
    p = mp.Process(target=worker, args=(child_conn,))
    p.start()

    # Send data from parent
    test_message = "Hello from the Zoo Master"
    print(f"[Master] Sending: {test_message}")
    parent_conn.send(test_message)

    # Receive response
    try:
        result = parent_conn.recv()
        print(f"[Master] Success! Received: {result}")
    except EOFError:
        print("[Master] Error: Pipe closed prematurely.")

    p.join()
    print("[Master] Test complete.")
