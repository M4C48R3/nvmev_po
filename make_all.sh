if [ "${1:-0}" != 0 ] # if argument is given clean. If not, it reinstalls the module without making
then
    echo "clean current repo and make"
    make clean
    make
fi

echo "Remove previously installed nvmev module"
sudo rmmod nvmev

echo "insert module"

if [ $(hostname -f) = "star3" ]
then
    # star3 server
    sudo insmod nvmev.ko memmap_start=128G memmap_size=32G cpus=1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16
else
    # desktop
    sudo insmod nvmev.ko memmap_start=16G memmap_size=24G cpus=1,2,3
fi