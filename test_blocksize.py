from subprocess import PIPE, run, Popen
try:
    import matplotlib.pyplot as plt
    import firebase_admin
    from firebase_admin import credentials, firestore, storage
    import socket
    import cpuinfo
    from PIL import Image 

except ImportError:
    run('python3 setup.py', stdout=PIPE, stderr=PIPE, universal_newlines=True, shell=True)
    import matplotlib.pyplot as plt
    import firebase_admin
    from firebase_admin import credentials, firestore, storage
    import socket
    import cpuinfo
    from PIL import Image 
    

def compute(block_sizes, matrix_size, repeats):
    out_times = list()

    for run_size in block_sizes:
        cmd = './bench_block ' + str(matrix_size) + ' ' + str(run_size) + ' ' + str(repeats)
        print(cmd)
        result = run(cmd, stdout=PIPE, stderr=PIPE, universal_newlines=True, shell=True)
        out = result.stdout
        num = float(out.strip())
        num = num / repeats
        out_times.append(num)
    
    return out_times


def init_firebase():
    cred = credentials.Certificate("cred.json")
    app = firebase_admin.initialize_app(cred, {'storageBucket': 'cache-sizing.appspot.com'})

    db = firestore.client()

    bucket = storage.bucket()

    return bucket, db


def put_host_data(db, hostname, sizes, times, cache_size_l2, cache_size_l3):
    db.collection(u'data').document(hostname).set({u'time': times, u'block size': sizes})
    db.collection(u'data').document(hostname).update({u'l2_cache': cache_size_l2, u'l3_cache': cache_size_l3})


def put_best_data(db, cache_size_l2, cache_size_l3, best_size, best_time, hostname):
    db.collection(u'l2').document(cache_size_l2).set({hostname: [best_time, best_size]}, merge=True)
    db.collection(u'l3').document(cache_size_l3).set({hostname: [best_time, best_size]}, merge=True)


def put_fig(bucket, hostname, filename):
    blob = bucket.blob(filename)
    blob.upload_from_filename(filename)



if __name__ == "__main__":
    bucket, db = init_firebase()
    hostname = socket.gethostname()
    print(hostname)

    filename = 'CacheTest-' + hostname + '.png'
    filename_line = 'CacheTest-' + hostname + '-line.png'
    
    cache_size_l3 = cpuinfo.get_cpu_info()['l3_cache_size']
    cache_size_l2 = cpuinfo.get_cpu_info()['l2_cache_size']
    print(cache_size_l2)
    print(cache_size_l3)

    # block_sizes = [4, 8, 16, 32, 64, 128, 256, 512, 1024]

    block_sizes = list()
    for i in range(2, 512):
        block_sizes.append(i*2)
    matrix_size = 2048
    repeats = 1

    out_times = compute(block_sizes, matrix_size, repeats)
    
    lowest_time = min(out_times)
    lowest_index = out_times.index(lowest_time)
    best_size = block_sizes[lowest_index]

    smaller = True
    while smaller:
        temp_list = list()
        try:
            block_sizes.index(best_size-1)
        except ValueError:
            temp_list.append(best_size-1)

        try:
            block_sizes.index(best_size+1)
        except ValueError:
            temp_list.append(best_size+1)

        print(temp_list)

        if len(temp_list) is 0:
            break

        temp_out = compute(temp_list, matrix_size, 3)

        smaller = False

        for item in temp_out:
            out_times.append(item)
            curr_block_size = temp_list[temp_out.index(item)]
            block_sizes.append(curr_block_size)

            if item < lowest_time:
                lowest_time = item
                best_size = curr_block_size
                smaller = True
                
    print(best_size)

    put_host_data(db, hostname, block_sizes, out_times, cache_size_l2, cache_size_l3)
    put_best_data(db, cache_size_l2, cache_size_l3, best_size, lowest_time, hostname)

    plt.scatter(block_sizes, out_times)
    plt.ylabel('Time (s)')
    plt.xlabel('Block Sizes')
    plt.savefig(filename)

    item_dict = dict(zip(block_sizes, out_times))

    sorted_list = sorted(item_dict.items())

    x, y = zip(*sorted_list)
    
    plt.plot(x, y)
    plt.ylabel('Time (s)')
    plt.xlabel('Block Sizes')    
    plt.savefig(filename_line)

    put_fig(bucket, hostname, filename_line)

    put_fig(bucket, hostname, filename)
