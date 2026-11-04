import psycopg
import threading
import time

PG_CONN = "postgresql://apple@localhost:5432/resumeiq"

def run_concurrency_tests():
    print("=" * 70)
    print("TASK 4: CONCURRENT DATABASE OPERATIONS & ISOLATION LEVEL AUDIT")
    print("=" * 70)

    test_cand_id = "cand-concurrency-test"
    with psycopg.connect(PG_CONN) as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM candidates WHERE id = %s", (test_cand_id,))
            cur.execute(
                "INSERT INTO candidates (id, name, email, total_experience_years) "
                "VALUES (%s, 'Concurrent Cand', 'concurrent@test.com', 5.0)",
                (test_cand_id,)
            )
            conn.commit()

    # TEST 1: Pessimistic Row Locking (SELECT ... FOR UPDATE)
    print("\n[Test 1] Pessimistic Row-Locking with SELECT ... FOR UPDATE")
    events = []

    def worker_1():
        with psycopg.connect(PG_CONN) as conn:
            with conn.cursor() as cur:
                events.append("Worker 1: BEGIN")
                cur.execute("BEGIN;")
                cur.execute(
                    "SELECT id, total_experience_years FROM candidates WHERE id = %s FOR UPDATE;",
                    (test_cand_id,)
                )
                events.append("Worker 1: Acquired exclusive row lock on candidate")
                time.sleep(0.3)  # Active processing window
                cur.execute(
                    "UPDATE candidates SET total_experience_years = total_experience_years + 1.0 WHERE id = %s;",
                    (test_cand_id,)
                )
                conn.commit()
                events.append("Worker 1: Updated +1.0 yr and COMMITTED (Lock Released)")

    def worker_2():
        time.sleep(0.08)  # Ensure worker 1 locks first
        with psycopg.connect(PG_CONN) as conn:
            with conn.cursor() as cur:
                events.append("Worker 2: Attempting SELECT ... FOR UPDATE (Must Block)")
                t0 = time.time()
                cur.execute("BEGIN;")
                cur.execute(
                    "SELECT id, total_experience_years FROM candidates WHERE id = %s FOR UPDATE;",
                    (test_cand_id,)
                )
                wait_time = time.time() - t0
                events.append(f"Worker 2: Unblocked and acquired lock after waiting {wait_time:.3f}s")
                cur.execute(
                    "UPDATE candidates SET total_experience_years = total_experience_years + 2.0 WHERE id = %s;",
                    (test_cand_id,)
                )
                conn.commit()
                events.append("Worker 2: Updated +2.0 yrs and COMMITTED")

    t1 = threading.Thread(target=worker_1)
    t2 = threading.Thread(target=worker_2)
    t1.start()
    t2.start()
    t1.join()
    t2.join()

    for e in events:
        print(f"  {e}")

    with psycopg.connect(PG_CONN) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT total_experience_years FROM candidates WHERE id = %s", (test_cand_id,))
            final_exp = cur.fetchone()[0]
            print(f"  Final Experience: {final_exp} (Expected: 5.0 + 1.0 + 2.0 = 8.0)")
            assert final_exp == 8.0, "Pessimistic locking failed!"

    # TEST 2: SERIALIZABLE ISOLATION LEVEL CONFLICT DETECTION (SSI)
    print("\n[Test 2] Serializable Snapshot Isolation (SSI) Serialization Failure")
    results = {}

    def ser_worker_1():
        try:
            with psycopg.connect(PG_CONN) as conn:
                with conn.cursor() as cur:
                    cur.execute("BEGIN TRANSACTION ISOLATION LEVEL SERIALIZABLE;")
                    cur.execute("SELECT total_experience_years FROM candidates WHERE id = %s;", (test_cand_id,))
                    cur.execute("UPDATE candidates SET total_experience_years = 15.0 WHERE id = %s;", (test_cand_id,))
                    time.sleep(0.25)
                    conn.commit()
                    results["worker_1"] = "COMMITTED"
        except Exception as e:
            results["worker_1"] = f"{e.sqlstate} - {str(e).strip()[:80]}"

    def ser_worker_2():
        time.sleep(0.08)  # Start while worker 1 is mid-transaction
        try:
            with psycopg.connect(PG_CONN) as conn:
                with conn.cursor() as cur:
                    cur.execute("BEGIN TRANSACTION ISOLATION LEVEL SERIALIZABLE;")
                    cur.execute("SELECT total_experience_years FROM candidates WHERE id = %s;", (test_cand_id,))
                    cur.execute("UPDATE candidates SET total_experience_years = 25.0 WHERE id = %s;", (test_cand_id,))
                    conn.commit()
                    results["worker_2"] = "COMMITTED"
        except Exception as e:
            results["worker_2"] = f"CAUGHT SERIALIZATION FAILURE ({e.sqlstate}): {str(e).strip()[:80]}"

    t1 = threading.Thread(target=ser_worker_1)
    t2 = threading.Thread(target=ser_worker_2)
    t1.start()
    t2.start()
    t1.join()
    t2.join()

    print(f"  Worker 1 status: {results.get('worker_1')}")
    print(f"  Worker 2 status: {results.get('worker_2')}")
    assert "CAUGHT SERIALIZATION FAILURE" in results.get("worker_2", ""), "SSI should reject concurrent update!"

    # Cleanup
    with psycopg.connect(PG_CONN) as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM candidates WHERE id = %s", (test_cand_id,))
            conn.commit()

    print("\n" + "=" * 70)
    print("TASK 4: CONCURRENCY & TRANSACTION ISOLATION FULLY VERIFIED!")
    print("=" * 70)

if __name__ == "__main__":
    run_concurrency_tests()
