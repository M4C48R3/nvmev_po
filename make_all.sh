attempts=1
max_attempts=10
while [ $attempts -le $max_attempts ]
do # start while loop attempts
echo "Remove previously installed nvmev module"
sudo rmmod nvmev

if [ "${1:-0}" != 0 ] # if argument is given clean. If not, it reinstalls the module without making
then
    echo "clean current repo and make"
    make clean
    make
fi

echo "insert module"

# CAUTION: ALSO UPDATE global_values.py!
if [ $(hostname -f) = "star3" ]
then
    # star3 server
    sudo insmod nvmev.ko memmap_start=128G memmap_size=96G cpus=1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16
elif [ $(hostname -f) = "streaming" ]
then
    # desktop
    sudo insmod nvmev.ko memmap_start=16G memmap_size=24G cpus=1,2,3
elif [ $(hostname -f) = "blaze51-Z790-PG-Lightning" ] || [ $(hostname -f) = "faduu2test" ]
then
    # desktop
    sudo insmod nvmev.ko memmap_start=12G memmap_size=40G cpus=1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16
elif [ $(hostname -f) = "gpu2" ]
then
    # gpu2 server
    sudo insmod nvmev.ko memmap_start=16G memmap_size=40G cpus=1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16
else
    echo "Unknown host: $(hostname -f)"
    attempts=9999
fi

# check if module is inserted: for some reason, the module is frequently not inserted in some machines.
if [ $(hostname -f) = "blaze51-Z790-PG-Lightning" ] || [ $(hostname -f) = "faduu2test" ]
then
    if sudo nvme list | grep -q "/dev/nvme3n1";
    then
        echo "module inserted: confirmed"
        attempts=9999
    else
        echo "module not inserted: /dev/nvme3n1 does not exist ($attempts/$max_attempts)"
        sudo rm /dev/nvme3n1
        attempts=$((attempts+1))
    fi
elif [ $(hostname -f) = "gpu2" ]
then
    if sudo nvme list | grep -q "/dev/nvme3n1";
    then
        echo "module inserted: confirmed"
        attempts=9999
    else
        echo "module not inserted: /dev/nvme3n1 does not exist ($attempts/$max_attempts)"
        sudo rm /dev/nvme3n1
        attempts=$((attempts+1))
    fi
else
    attempts=9999
fi

done # end while loop attempts