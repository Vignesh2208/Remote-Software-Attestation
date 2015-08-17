obj-m := Attestation_module.o
Attestation_module-objs := Attestation_kernel_module.o Read_process_memory_map.o 

all:
	make -C /lib/modules/$(shell uname -r)/build M=$(shell pwd) modules
clean:
	make -C /lib/modules/$(shell uname -r)/build M=$(shell pwd) clean
