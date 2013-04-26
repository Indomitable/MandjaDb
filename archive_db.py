import gzip

__author__ = 'vmladenov'
from lzma import LZMACompressor

if __name__ == "__main__":
    path = "cook.db"
    path_compressed = "cook_compressed.gz"

    # chunk = 8 * 1024
    # data = []
    # with open(path, "rb") as fr:
    #     data = fr.read()
    #     # data_chunk = fr.read(chunk)
    #     # while data_chunk:
    #     #     data += data_chunk
    #     #     data_chunk = fr.read(chunk)
    #     fr.close()
    # print("Raw: " + str(len(data)))
    # # compressor = LZMACompressor()
    # # compressed_data = compressor.compress(bytes(data))
    # # compressed_data += compressor.flush()
    #
    # print("Compressed: " + str(len(compressed_data)))
    # with open(path_compressed, "wb") as fw:
    #     fw.write(compressed_data)
    #     fw.flush()
    #     fw.close()

    f_in = open(path, 'rb')
    f_out = gzip.open(path_compressed, 'wb')
    f_out.writelines(f_in)
    f_out.close()
    f_in.close()


    print("Finish")
