package org.example.repository;

import org.example.entity.Specialist;

import java.util.UUID;

public interface SpecialistRepository extends CrudRepository<Specialist, UUID> {
    Specialist readWithTeam(Specialist entity);

    Specialist readWithWorkPlans(Specialist entity);
}
