import firebase_admin
from firebase_admin import credentials, firestore, storage
import matplotlib.pyplot as plt

num_figures = 1

def init_firebase():
    cred = credentials.Certificate("cache-sizing-firebase-adminsdk-6vjhk-1a40ccc709.json")
    app = firebase_admin.initialize_app(cred, {'storageBucket': 'cache-sizing.appspot.com'})

    db = firestore.client()

    bucket = storage.bucket()

    return bucket, db


def get_cache_sizes(db, level):
    col_ref = db.collection(level)
    level_caches = col_ref.list_documents()
    return_list = list()
    for level_cache in level_caches:
        split_cache = level_cache.id.split()
        if split_cache[1] == 'MiB':
            kilobytes = int(float(split_cache[0]) * 1000000)
        else:
            kilobytes = int(float(split_cache[0]) * 1000)
        data = level_cache.get().to_dict()
        return_list.append((kilobytes, data))
    return return_list


def put_fig(bucket, filename):
    blob = bucket.blob(filename)
    blob.upload_from_filename(filename)


def plot_data(x, y, name, xlabel, ylabel, bucket, scatter=True, line=True, upload=True, show=False):
    global num_figures

    item_dict = dict(zip(x, y))

    sorted_list = sorted(item_dict.items())

    x, y = zip(*sorted_list)

    if scatter:
        plt.figure(num_figures)
        plt.scatter(x, y)
        plt.title(name)
        plt.ylabel(ylabel)
        plt.xlabel(xlabel)
        plt.savefig(name + '-scatter.png')
        if show:
            plt.show()
        num_figures += 1

    if line:
        plt.figure(num_figures)
        plt.plot(x, y)
        plt.title(name)
        plt.ylabel(ylabel)
        plt.xlabel(xlabel)
        plt.savefig(name + '-line.png') 
        if show:
            plt.show() 
        num_figures += 1

    if upload:
        if scatter:
            put_fig(bucket, name + '-scatter.png')  
        if line:
            put_fig(bucket, name + '-line.png')  



def get_host_data(db):   
    data_docs = db.collection(u'data').list_documents()
    out_dict = dict()
    for doc in data_docs:
        data_dict = doc.get().to_dict()
        out_dict[doc.id] = data_dict
    return out_dict


def build_cache_data(data):
    cache_sizes = list()
    times = list()
    block_sizes = list()
    for cache_size in data:
        size = cache_size[0]
        for host in cache_size[1]:
            host_data = cache_size[1][host]
            cache_sizes.append(size)
            times.append(host_data[0])
            block_sizes.append(host_data[1])
    return cache_sizes, times, block_sizes



if __name__ == "__main__":
    bucket, db = init_firebase()

    l2_cache_data = get_cache_sizes(db, 'l2')
    l3_cache_data = get_cache_sizes(db, 'l3')

    host_data = get_host_data(db)

    # Level 2 Cache

    title = 'Cache Sizes to best preforming block size (L2)'
    cache_sizes, times, block_sizes = build_cache_data(l2_cache_data)
    plot_data(cache_sizes, block_sizes, title, 'Cache Sizes', 'Best block size', bucket, line=False)

    title = 'Cache Sizes to time (s) (L2)'
    plot_data(cache_sizes, times, title, 'Cache Sizes', 'Time (s)', bucket)

    # Level 3 Cache

    title = 'Cache Sizes to best preforming block size (L3)'
    cache_sizes, times, block_sizes = build_cache_data(l3_cache_data)
    plot_data(cache_sizes, block_sizes, title, 'Cache Sizes', 'Best block size', bucket, line=False)

    title = 'Cache Sizes to time (s) (L3)'
    plot_data(cache_sizes, times, title, 'Cache Sizes', 'Time (s)', bucket)

    # Host Data

    for host in host_data:
        title = 'Time to Block Size - ' + host
        plot_data(host_data[host]['block size'], host_data[host]['time'], title, 'Block Sizes', 'Time (s)', bucket)

