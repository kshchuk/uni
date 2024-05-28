package com.example.publicutilitiesapi.service;

import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;
import java.util.Optional;
import java.util.UUID;

public abstract class CrudService<T, ID> {

    protected abstract JpaRepository<T, ID> getRepository();

    public List<T> findAll() {
        return getRepository().findAll();
    }

    public Optional<T> findById(ID id) {
        return getRepository().findById(id);
    }

    public T save(T entity) {
        return getRepository().save(entity);
    }

    public void deleteById(ID id) {
        getRepository().deleteById(id);
    }
}
