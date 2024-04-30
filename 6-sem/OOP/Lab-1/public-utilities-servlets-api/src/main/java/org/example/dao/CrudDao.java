package org.example.dao;

import java.util.List;

public interface CrudDao<T, Id> {
    T create(T entity) throws Exception;
    T read(Id id) throws Exception;
    void update(T entity) throws Exception;
    void delete(Id id) throws Exception;
    List<T> findAll() throws Exception;

}
