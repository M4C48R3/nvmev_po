sudo fio --filename="/dev/nvme1n1" --direct=1 --rw=write --ioengine=psync --bs=4k --iodepth=1 --io_size=1G --name=fio_direct_write_test
echo "+++"
sudo fio --filename="/dev/nvme1n1" --direct=1 --rw=read --ioengine=psync --bs=4k --iodepth=1 --io_size=1G --name=fio_direct_read_test
echo "+++"
sudo fio --filename="/dev/nvme0n1" --direct=1 --rw=write --ioengine=psync --bs=4k --iodepth=1 --io_size=1G --name=fio_direct_write_test
echo "+++"
sudo fio --filename="/dev/nvme0n1" --direct=1 --rw=read --ioengine=psync --bs=4k --iodepth=1 --io_size=1G --name=fio_direct_read_test
echo "+++"


sudo fio --filename="/dev/nvme1n1" --direct=1 --rw=write --ioengine=psync --bs=8k --iodepth=1 --io_size=1G --name=fio_direct_write_test
echo "+++"
sudo fio --filename="/dev/nvme1n1" --direct=1 --rw=read --ioengine=psync --bs=8k --iodepth=1 --io_size=1G --name=fio_direct_read_test
echo "+++"

sudo fio --filename="/dev/nvme0n1" --direct=1 --rw=write --ioengine=psync --bs=8k --iodepth=1 --io_size=1G --name=fio_direct_write_test
echo "+++"
sudo fio --filename="/dev/nvme0n1" --direct=1 --rw=read --ioengine=psync --bs=8k --iodepth=1 --io_size=1G --name=fio_direct_read_test
echo "+++"


sudo fio --filename="/dev/nvme1n1" --direct=1 --rw=write --ioengine=psync --bs=16k --iodepth=1 --io_size=1G --name=fio_direct_write_test
echo "+++"
sudo fio --filename="/dev/nvme1n1" --direct=1 --rw=read --ioengine=psync --bs=16k --iodepth=1 --io_size=1G --name=fio_direct_read_test
echo "+++"

sudo fio --filename="/dev/nvme0n1" --direct=1 --rw=write --ioengine=psync --bs=16k --iodepth=1 --io_size=1G --name=fio_direct_write_test
echo "+++"
sudo fio --filename="/dev/nvme0n1" --direct=1 --rw=read --ioengine=psync --bs=16k --iodepth=1 --io_size=1G --name=fio_direct_read_test
echo "+++"


sudo fio --filename="/dev/nvme1n1" --direct=1 --rw=write --ioengine=psync --bs=32k --iodepth=1 --io_size=1G --name=fio_direct_write_test
echo "+++"
sudo fio --filename="/dev/nvme1n1" --direct=1 --rw=read --ioengine=psync --bs=32k --iodepth=1 --io_size=1G --name=fio_direct_read_test
echo "+++"

sudo fio --filename="/dev/nvme0n1" --direct=1 --rw=write --ioengine=psync --bs=32k --iodepth=1 --io_size=1G --name=fio_direct_write_test
echo "+++"
sudo fio --filename="/dev/nvme0n1" --direct=1 --rw=read --ioengine=psync --bs=32k --iodepth=1 --io_size=1G --name=fio_direct_read_test
echo "+++"


sudo fio --filename="/dev/nvme1n1" --direct=1 --rw=write --ioengine=psync --bs=64k --iodepth=1 --io_size=2G --name=fio_direct_write_test
echo "+++"
sudo fio --filename="/dev/nvme1n1" --direct=1 --rw=read --ioengine=psync --bs=64k --iodepth=1 --io_size=2G --name=fio_direct_read_test
echo "+++"

sudo fio --filename="/dev/nvme0n1" --direct=1 --rw=write --ioengine=psync --bs=64k --iodepth=1 --io_size=2G --name=fio_direct_write_test
echo "+++"
sudo fio --filename="/dev/nvme0n1" --direct=1 --rw=read --ioengine=psync --bs=64k --iodepth=1 --io_size=2G --name=fio_direct_read_test
echo "+++"


sudo fio --filename="/dev/nvme1n1" --direct=1 --rw=write --ioengine=psync --bs=128k --iodepth=1 --io_size=2G --name=fio_direct_write_test
echo "+++"
sudo fio --filename="/dev/nvme1n1" --direct=1 --rw=read --ioengine=psync --bs=128k --iodepth=1 --io_size=2G --name=fio_direct_read_test
echo "+++"

sudo fio --filename="/dev/nvme0n1" --direct=1 --rw=write --ioengine=psync --bs=128k --iodepth=1 --io_size=2G --name=fio_direct_write_test
echo "+++"
sudo fio --filename="/dev/nvme0n1" --direct=1 --rw=read --ioengine=psync --bs=128k --iodepth=1 --io_size=2G --name=fio_direct_read_test

echo "+++"

sudo fio --filename="/dev/nvme1n1" --direct=1 --rw=write --ioengine=psync --bs=256k --iodepth=1 --io_size=2G --name=fio_direct_write_test
echo "+++"
sudo fio --filename="/dev/nvme1n1" --direct=1 --rw=read --ioengine=psync --bs=256k --iodepth=1 --io_size=2G --name=fio_direct_read_test

echo "+++"
sudo fio --filename="/dev/nvme0n1" --direct=1 --rw=write --ioengine=psync --bs=256k --iodepth=1 --io_size=2G --name=fio_direct_write_test
echo "+++"
sudo fio --filename="/dev/nvme0n1" --direct=1 --rw=read --ioengine=psync --bs=256k --iodepth=1 --io_size=2G --name=fio_direct_read_test
