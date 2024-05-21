package org.example.mapper;

public interface MapperBase<E, D> {
    E toEntity(D dto);
    D toDto(E entity);
}
