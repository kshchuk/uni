package org.example.repository;

import org.example.entity.Request;

import java.util.UUID;

public interface RequestRepository extends CrudRepository<Request, UUID> {
}
