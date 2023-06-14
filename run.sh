sudo fio --filename="/dev/nvme1n1" --direct=1 --rw=write --ioengine=psync --bs=4k --iodepth=1 --io_size=1G --name=fio_direct_write_test
