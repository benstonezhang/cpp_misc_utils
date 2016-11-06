//
// Created by Benstone on 16/11/6.
//

#ifndef HAVE_ANONYMOUS_SEMAPHORE

#include <sys/types.h>
#include <string.h>
#include <unistd.h>
#include <dlfcn.h>
#include <pthread.h>
#include <semaphore.h>
#include <stdio.h>
#include <assert.h>

#ifndef MAX_ANONMOUS_SEMAPHORE
#define MAX_ANONMOUS_SEMAPHORE    16
#endif

#ifndef OSX_ANON_SEM_NAME_PREFIX
#define OSX_ANON_SEM_NAME_PREFIX "/AnonSem"
#endif

#define OSX_POSIX_SEM_NAME_LEN 32

static const char *sem_prefix = OSX_ANON_SEM_NAME_PREFIX;
static int is_mutex_inited = 0;
static pthread_mutex_t sem_ptr_mutex;
static int sem_id = 0;
static sem_t *sem_list[MAX_ANONMOUS_SEMAPHORE];

int sem_init(sem_t *sem, int pshared, unsigned int value) {
	assert(sem != NULL);

	pid_t pid;
	int id;
	char sem_name[OSX_POSIX_SEM_NAME_LEN];

	if (is_mutex_inited == 0) {
		pthread_mutex_init(&sem_ptr_mutex, NULL);
		is_mutex_inited = 1;
	}

	pthread_mutex_lock(&sem_ptr_mutex);
	id = sem_id++;
	pthread_mutex_unlock(&sem_ptr_mutex);

	pid = getpid();
	snprintf(sem_name, sizeof(sem_name), "%s/%d/%d", sem_prefix, pid, id);
	sem_unlink(sem_name);
	sem_t *sem_ptr = sem_open(sem_name, O_CREAT | O_EXCL, pshared, value);
	if (sem_ptr == NULL) {
		return -1;
	}

	sem_list[id] = sem_ptr;
	*sem = id;

	return 0;
}

int sem_destroy(sem_t *sem) {
	assert(sem != NULL);
	assert(((*sem) >= 0) && ((*sem) < MAX_ANONMOUS_SEMAPHORE));

	int id = *sem;
	sem_t *sem_ptr = sem_list[id];
	sem_list[id] = NULL;
	sem_close(sem_ptr);

	char sem_name[OSX_POSIX_SEM_NAME_LEN];
	pid_t pid = getpid();
	snprintf(sem_name, sizeof(sem_name), "%s/%d/%d", sem_prefix, pid, id);
	return sem_unlink(sem_name);
}

typedef int (*sem_func_ptr)(sem_t *);

int sem_post(sem_t *sem) {
	assert(sem != NULL);
	assert(((*sem) >= 0) && ((*sem) < MAX_ANONMOUS_SEMAPHORE));

	sem_func_ptr post_ptr = (sem_func_ptr)dlsym(RTLD_NEXT, __func__);
	sem_t *sem_ptr = sem_list[*sem];
	return (*post_ptr)(sem_ptr);
}

int sem_trywait(sem_t * sem) {
	assert(sem != NULL);
	assert(((*sem) >= 0) && ((*sem) < MAX_ANONMOUS_SEMAPHORE));

	sem_func_ptr trywait_ptr = (sem_func_ptr)dlsym(RTLD_NEXT, __func__);
	sem_t *sem_ptr = sem_list[*sem];
	return (*trywait_ptr)(sem_ptr);
}

int sem_wait(sem_t * sem) {
	assert(sem != NULL);
	assert(((*sem) >= 0) && ((*sem) < MAX_ANONMOUS_SEMAPHORE));

	sem_func_ptr wait_ptr = (sem_func_ptr)dlsym(RTLD_NEXT, __func__);
	sem_t *sem_ptr = sem_list[*sem];
	return (*wait_ptr)(sem_ptr);
}

#endif
