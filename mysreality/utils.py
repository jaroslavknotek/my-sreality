from tqdm.auto import tqdm
import multiprocessing as mp


def parallel(fn, args, desc=None, progress=True, processes=None):
    n = len(args)
    with mp.Pool(processes) as pool:
        job_iter = pool.imap(fn, args)
        if progress:
            job_iter = tqdm(job_iter, desc=desc, total=n)
        return list(job_iter)
