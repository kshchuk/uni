package com.example.publicutilitiesapi.mapper;

public interface MapperBase<D, E> {
    D toDto(E entity);
    E toEntity(D dto);
}
