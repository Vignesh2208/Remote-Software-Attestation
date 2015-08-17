#include <linux/init.h>
#include <linux/kernel.h>
#include <linux/module.h>
#include <linux/sched.h>
#include <linux/mm.h>
#include <linux/slab.h>
#include <asm/uaccess.h> /* for copy_*_user */

static void print_mem(struct task_struct *task);
extern int process_memory_map_load(char * kernel_buffer, int * size);
static int isvalid(char character);
static int parse_input(char * buffer) ;
