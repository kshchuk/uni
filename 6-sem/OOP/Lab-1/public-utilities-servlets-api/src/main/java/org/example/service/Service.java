package org.example.service;

import java.util.List;

public interface Service<T, Id> {
    void create(T t);
    T get(Id id);
    void update(T t);
    boolean delete(Id id);
    List<T> getAll();
}
