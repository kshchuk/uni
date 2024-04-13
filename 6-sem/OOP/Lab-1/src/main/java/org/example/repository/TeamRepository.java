package org.example.repository;

import org.example.entity.Team;

import java.util.UUID;

public interface TeamRepository extends CrudRepository<Team, UUID>{
    Team readWithDispatcher(Team entity);

    Team readWithSpecialists(Team entity);

    Team readWithWorkPlans(Team entity);
}
