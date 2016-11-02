//
// Created by Benstone on 16/5/16.
//

#include <dlfcn.h>
#include <pthread.h>
#include <semaphore.h>

#include <cstring>
#include <map>

static bool is_mutex_inited = false;
static pthread_mutex_t sem_ptr_mutex;
static std::map<int, sem_t *> sem_ptrs;
static int sem_id = 0;
static const char *sem_prefix = "/AnonSem_";

int sem_init(sem_t *sem, int pshared, unsigned int value) {
	int id;
	char sem_name[strlen(sem_prefix) + 16];

	if (!is_mutex_inited) {
		pthread_mutex_init(&sem_ptr_mutex, NULL);
	}

	pthread_mutex_lock(&sem_ptr_mutex);
	id = sem_id++;
	pthread_mutex_unlock(&sem_ptr_mutex);

	sprintf(sem_name, "%s%d", sem_prefix, id);
	sem_unlink(sem_name);
	sem_t *sem_ptr = sem_open(sem_name, O_CREAT, pshared, value);
	if (sem_ptr == NULL) {
		return -1;
	}

	pthread_mutex_lock(&sem_ptr_mutex);
	sem_ptrs.insert(std::pair<int, sem_t *>(id, sem_ptr));
	pthread_mutex_unlock(&sem_ptr_mutex);

	*sem = id;
	return 0;
}

int sem_destroy(sem_t *sem) {
	char sem_name[strlen(sem_prefix) + 16];

	pthread_mutex_lock(&sem_ptr_mutex);
	int id = *sem;
	sem_t *sem_ptr = sem_ptrs[id];
	sem_ptrs.erase(id);
	pthread_mutex_unlock(&sem_ptr_mutex);

	sprintf(sem_name, "%s%d", sem_prefix, id);
	sem_close(sem_ptr);
	return sem_unlink(sem_name);
}

typedef int (*sem_func_ptr)(sem_t *);

int sem_post(sem_t *sem) {
	pthread_mutex_lock(&sem_ptr_mutex);
	sem_t *sem_ptr = sem_ptrs[*sem];
	pthread_mutex_unlock(&sem_ptr_mutex);
	sem_func_ptr post_ptr = (sem_func_ptr)dlsym(RTLD_NEXT, "sem_post");
	return (*post_ptr)(sem_ptr);
}

int sem_trywait(sem_t * sem) {
	pthread_mutex_lock(&sem_ptr_mutex);
	sem_t *sem_ptr = sem_ptrs[*sem];
	pthread_mutex_unlock(&sem_ptr_mutex);
	sem_func_ptr trywait_ptr = (sem_func_ptr)dlsym(RTLD_NEXT, "sem_trywait");
	return (*trywait_ptr)(sem_ptr);
}

int sem_wait(sem_t * sem) {
	pthread_mutex_lock(&sem_ptr_mutex);
	sem_t *sem_ptr = sem_ptrs[*sem];
	pthread_mutex_unlock(&sem_ptr_mutex);
	sem_func_ptr wait_ptr = (sem_func_ptr)dlsym(RTLD_NEXT, "sem_wait");
	return (*wait_ptr)(sem_ptr);
}

