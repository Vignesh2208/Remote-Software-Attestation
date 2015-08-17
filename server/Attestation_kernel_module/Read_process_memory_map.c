#include "Read_process_memory_map.h"
#include <linux/crypto.h>
#include <linux/err.h>
#include <linux/scatterlist.h>
#define MAX_NO_OF_VALID_CHARACTERS 11
#define MAX_NO_OF_BYTE_SELECTIONS 100
#define MAX_SIZE_OF_EACH_SELECTION 20
#define PROCFS_MAX_SIZE 2048


static int pid_mem = 1;
static int no_of_byte_selections = 0;
static int actual_number_of_byte_selections = 0;
static char valid_chars[MAX_NO_OF_VALID_CHARACTERS];
static char data_stream_buffer[MAX_SIZE_OF_EACH_SELECTION]; // Used to hold each number extracted from /proc/Attest. It can hold atmost a 19 digit 
//number with each digit at an index
static int byte_position_buffer[MAX_NO_OF_BYTE_SELECTIONS];

//static int * byte_position_buffer;
static void cleanup()
{	
	int i = 0;
	
	for(i=0;i < MAX_SIZE_OF_EACH_SELECTION;i++)
		data_stream_buffer[i] = NULL;

	
	actual_number_of_byte_selections = 0;
	no_of_byte_selections = 0;
	printk(KERN_INFO "\n Clean up finished");

	
} 
static void print_mem_map(struct task_struct *task, char * kernel_buffer, int * kernel_buffer_length)
{
	struct mm_struct *mm;
        struct vm_area_struct *vma;
	int num_of_bytes_uncopied,offset;
	char copied_byte_value;
        int count = 0, i =0;
        mm = task->mm;

	struct scatterlist sg;
	struct hash_desc desc;
	size_t len;
	char hashtext[41];
	char hash_input_string[sizeof(int)*MAX_NO_OF_BYTE_SELECTIONS];
	
	i = 0;
	while(i<40){
		hashtext[i] = NULL;
		i++;
	}

	for(i=0; i < sizeof(int)*MAX_NO_OF_BYTE_SELECTIONS; i++)
		hash_input_string[i] = NULL;
		


	
        printk("\nThis mm_struct has %d vmas.\n", mm->map_count);
        for (vma = mm->mmap ; vma ; vma = vma->vm_next) {
                printk ("\nVma number %d: \n", ++count);
                printk("  Starts at 0x%lx, Ends at 0x%lx\n",
                           vma->vm_start, vma->vm_end);
       }
       printk("\nCode  Segment start = 0x%lx, end = 0x%lx \n"
                 "Data  Segment start = 0x%lx, end = 0x%lx\n"
                 "Stack Segment start = 0x%lx\n",
                 mm->start_code, mm->end_code,
                 mm->start_data, mm->end_data,
                 mm->start_stack);

	
	if(no_of_byte_selections != actual_number_of_byte_selections){
			printk(KERN_INFO "\n Proc file written in improper format. Number of indicated byte selections which is %d does not match the actual number of byte selections which is %d \n",no_of_byte_selections,actual_number_of_byte_selections);
	}
	else{
		for(i = 0 ; i< actual_number_of_byte_selections; i++){
			offset = byte_position_buffer[i];
			if(offset){
				num_of_bytes_uncopied = copy_from_user(&byte_position_buffer[i],mm->start_code + offset,1);	
			if(num_of_bytes_uncopied == 0 )
				printk(KERN_INFO "\n Code content: Byte offset %d. Value at offset : %x",offset,(unsigned char)byte_position_buffer[i]);
			hash_input_string[i] = byte_position_buffer[i] ;
				printk(KERN_INFO "\n Hash input value : %x", (unsigned char ) hash_input_string[i]);
		
			}
	        }

		i = 0;
		len = 0;
		len = actual_number_of_byte_selections;
		//while(hash_input_string[i] != NULL){
		//	len++;
		//	i++;
		//}
		sg_init_one(&sg, hash_input_string, len);
		desc.tfm = crypto_alloc_hash("sha1", 0, CRYPTO_ALG_ASYNC);
		crypto_hash_init(&desc);
		crypto_hash_update(&desc, &sg, len);
		crypto_hash_final(&desc, hashtext);

		printk(KERN_INFO "\n SHA1 - hash computed ");
		i = 0;
		while(i <= 19){
			printk(KERN_INFO "%x, counter = %d",(unsigned char) hashtext[i],i);
			i++;
		}

		crypto_free_hash(desc.tfm);

		for(i = 0; i < PROCFS_MAX_SIZE; i++)
			kernel_buffer[i] = NULL;
		memcpy(kernel_buffer,hashtext,20);
		//*kernel_buffer_length = 5;
			
		
	}

	
}

int process_memory_map_load(char * kernel_buffer, int * kernel_buffer_length){
        struct task_struct *task;
	
	//printk(KERN_INFO "\n Inside process_memory_map load. Input %s",kernel_buffer);

	if(parse_input(kernel_buffer) != 0){
		printk(KERN_INFO "\n Input not in proper format");
		return 0;
	}
	else {
	        
		//kstrtoint(kernel_buffer,0,&pid_mem);
		printk("\nGot the process id to look up as %d.\n", pid_mem);
        	for_each_process(task) {
        	         if ( task->pid == pid_mem) {
        	                 printk("%s[%d]\n", task->comm, task->pid);
        	                 print_mem_map(task,kernel_buffer,kernel_buffer_length);
				 // Done with this. Cleanup
				cleanup();
				
        	         }
        	}
	}        
	return 0;
}

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


static int set_fields(int space_count){
	int byte_position = 0;
	char * end_ptr;
	
	if(space_count == 1){
		
		pid_mem = simple_strtol(data_stream_buffer,&end_ptr,10);
		printk(KERN_INFO "\n Decoded process id %d",pid_mem);
	}
	else{
		if(space_count == 2){
			
			no_of_byte_selections = simple_strtol(data_stream_buffer,&end_ptr,10);
			printk(KERN_INFO "\n Decoded number of byte selections %d",no_of_byte_selections);
			if(no_of_byte_selections > MAX_NO_OF_BYTE_SELECTIONS)
				no_of_byte_selections = MAX_NO_OF_BYTE_SELECTIONS; // Cap it off here
			
			
			

		}
		else{
			if(no_of_byte_selections < 0)
				return -1 ; // Error
			actual_number_of_byte_selections  = space_count - 2;
			if(actual_number_of_byte_selections > no_of_byte_selections)
				return -1; // Error. To prevent buffer overflow			
			
			byte_position = simple_strtol(data_stream_buffer,&end_ptr,10);
			byte_position_buffer[space_count-3] = byte_position;
			printk(KERN_INFO "\n Counter : %d decoded byte position %d",space_count-2,byte_position);
				
		}

	}
	
	
	

	return 1;
}
static int parse_input(char * buffer) {
	init_digit_array();
	int index = 0, i = 0,j = 0;
	int space_count = 0,prev_start_index = 0;
	
	while(buffer[index] != NULL) {
		
		if(isvalid(buffer[index]) != 0 && buffer[index] != ' ')
			return -1; // Error	
		else{
			if(buffer[index] == ' ' && index != 0){
				space_count ++;
				printk(KERN_INFO "\n Space count %d, Index %d",space_count,index);
				
				if(index - prev_start_index > MAX_SIZE_OF_EACH_SELECTION)
				{
					printk(KERN_INFO "\n Entry in the proc file too large. Exiting ");
					return -1 ; // Error
				}
				j = 0;
				for(i = prev_start_index; i < index; i++){
					data_stream_buffer[j] = buffer[i];
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
		
	
	
	return 0; // All characters are valid

}

