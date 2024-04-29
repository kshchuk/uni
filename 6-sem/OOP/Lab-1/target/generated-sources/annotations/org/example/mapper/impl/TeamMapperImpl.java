package org.example.mapper.impl;

import java.util.List;
import java.util.UUID;
import javax.annotation.processing.Generated;
import org.example.dto.TeamDTO;
import org.example.entity.Specialist;
import org.example.entity.Team;
import org.example.entity.WorkPlan;
import org.example.mapper.TeamMapper;

@Generated(
    value = "org.mapstruct.ap.MappingProcessor",
    date = "2024-04-29T15:01:53+0300",
    comments = "version: 1.5.5.Final, compiler: javac, environment: Java 21.0.2 (Oracle Corporation)"
)
public class TeamMapperImpl implements TeamMapper {

    @Override
    public TeamDTO toDto(Team team) {
        if ( team == null ) {
            return null;
        }

        TeamDTO teamDTO = new TeamDTO();

        List<String> list = mapTeamSpecialistListToStringList( team.getSpecialists() );
        if ( list != null ) {
            teamDTO.setSpecialistIds( list );
        }
        List<String> list1 = mapTeamWorkPlanListToStringList( team.getWorkPlans() );
        if ( list1 != null ) {
            teamDTO.setWorkPlanIds( list1 );
        }
        if ( team.getDispatcher() != null ) {
            teamDTO.setDispatcherId( mapTeamDispatcherToString( team.getDispatcher() ) );
        }
        if ( team.getTeamId() != null ) {
            teamDTO.setTeamId( team.getTeamId().toString() );
        }

        return teamDTO;
    }

    @Override
    public Team toEntity(TeamDTO teamDTO) {
        if ( teamDTO == null ) {
            return null;
        }

        Team team = new Team();

        List<Specialist> list = mapTeamStringListToSpecialistList( teamDTO.getSpecialistIds() );
        if ( list != null ) {
            team.setSpecialists( list );
        }
        List<WorkPlan> list1 = mapTeamStringListToWorkPlanList( teamDTO.getWorkPlanIds() );
        if ( list1 != null ) {
            team.setWorkPlans( list1 );
        }
        if ( teamDTO.getDispatcherId() != null ) {
            team.setDispatcher( mapTeamStringToDispatcher( teamDTO.getDispatcherId() ) );
        }
        if ( teamDTO.getTeamId() != null ) {
            team.setTeamId( UUID.fromString( teamDTO.getTeamId() ) );
        }

        return team;
    }
}
