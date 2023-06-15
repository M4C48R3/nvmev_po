echo "clean current repo and make"
make clean
make

echo "Remove previously installed nvmev module"
sudo rmmod nvmev

#echo "verify virtual device is removed"
#sudo nvme list

echo "insert module"
sudo insmod nvmev.ko memmap_start=4G memmap_size=1G cpus=3,4

#echo "verify device is made"
#sudo nvme list

# echo ""
# echo "------------------------------------------------------------------------"
# echo "------------------------------------------------------------------------"
# echo ""
# echo "SEQ READ"
# echo "sudo fio --filename="/dev/nvme1n1" --direct=1 --rw=read --ioengine=psync --bs=4k --iodepth=1 --size=1G --name=fio_seq_read_test"
# sudo fio --filename="/dev/nvme1n1" --direct=1 --rw=read --ioengine=psync --bs=4k --iodepth=1 --size=1G --name=fio_seq_read_test
# echo ""
# echo "------------------------------------------------------------------------"
# echo ""
# echo "RAND READ" 
# echo "sudo fio --filename="/dev/nvme1n1" --direct=1 --rw=randread --ioengine=psync --bs=4k --iodepth=1 --size=1G --name=fio_rand_read_test"
# sudo fio --filename="/dev/nvme1n1" --direct=1 --rw=randread --ioengine=psync --bs=4k --iodepth=1 --size=1G --name=fio_rand_read_test
# echo ""
# echo "------------------------------------------------------------------------"
# echo ""
# echo "SEQ WRITE"
# echo "sudo fio --filename="/dev/nvme1n1" --direct=1 --rw=write --ioengine=psync --bs=4k --iodepth=1 --size=1G --name=fio_seq_write_test"
# sudo fio --filename="/dev/nvme1n1" --direct=1 --rw=write --ioengine=psync --bs=4k --iodepth=1 --size=1G --name=fio_seq_write_test
# echo ""
# echo "------------------------------------------------------------------------"
# echo ""
# echo "RAND WRITE"
# echo "sudo fio --filename="/dev/nvme1n1" --direct=1 --rw=write --ioengine=psync --bs=4k --iodepth=1 --size=1G --name=fio_rand_write_test"
# sudo fio --filename="/dev/nvme1n1" --direct=1 --rw=write --ioengine=psync --bs=4k --iodepth=1 --size=1G --name=fio_rand_write_test

