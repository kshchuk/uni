package org.example.mapper.impl;

import java.time.Duration;
import java.util.UUID;
import javax.annotation.processing.Generated;
import org.example.dto.WorkPlanDTO;
import org.example.entity.WorkPlan;
import org.example.mapper.WorkPlanMapper;

@Generated(
    value = "org.mapstruct.ap.MappingProcessor",
    date = "2024-04-29T15:01:53+0300",
    comments = "version: 1.5.5.Final, compiler: javac, environment: Java 21.0.2 (Oracle Corporation)"
)
public class WorkPlanMapperImpl implements WorkPlanMapper {

    @Override
    public WorkPlanDTO toDto(WorkPlan workPlan) {
        if ( workPlan == null ) {
            return null;
        }

        WorkPlanDTO workPlanDTO = new WorkPlanDTO();

        if ( workPlan.getTeam() != null ) {
            workPlanDTO.setTeamId( mapTeamId( workPlan.getTeam() ) );
        }
        if ( workPlan.getWorkPlanId() != null ) {
            workPlanDTO.setWorkPlanId( workPlan.getWorkPlanId().toString() );
        }
        if ( workPlan.getDescription() != null ) {
            workPlanDTO.setDescription( workPlan.getDescription() );
        }
        if ( workPlan.getDuration() != null ) {
            workPlanDTO.setDuration( workPlan.getDuration().toString() );
        }

        return workPlanDTO;
    }

    @Override
    public WorkPlan toEntity(WorkPlanDTO workPlanDTO) {
        if ( workPlanDTO == null ) {
            return null;
        }

        WorkPlan workPlan = new WorkPlan();

        if ( workPlanDTO.getTeamId() != null ) {
            workPlan.setTeam( mapTeam( workPlanDTO.getTeamId() ) );
        }
        if ( workPlanDTO.getWorkPlanId() != null ) {
            workPlan.setWorkPlanId( UUID.fromString( workPlanDTO.getWorkPlanId() ) );
        }
        if ( workPlanDTO.getDescription() != null ) {
            workPlan.setDescription( workPlanDTO.getDescription() );
        }
        if ( workPlanDTO.getDuration() != null ) {
            workPlan.setDuration( Duration.parse( workPlanDTO.getDuration() ) );
        }

        return workPlan;
    }
}
