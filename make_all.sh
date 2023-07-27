if [ "${1:-0}" != 0 ] # if argument is given clean. If not, it reinstalls the module without making
then
    echo "clean current repo and make"
    make clean
    make
fi

echo "Remove previously installed nvmev module"
sudo rmmod nvmev

echo "insert module"
sudo insmod nvmev.ko memmap_start=16G memmap_size=24G cpus=1,2,3