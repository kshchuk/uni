package org.example.mapper.impl;

import java.util.List;
import java.util.UUID;
import javax.annotation.processing.Generated;
import org.example.dto.SpecialistDTO;
import org.example.entity.Specialist;
import org.example.entity.WorkPlan;
import org.example.mapper.SpecialistMapper;

@Generated(
    value = "org.mapstruct.ap.MappingProcessor",
    date = "2024-04-29T15:01:54+0300",
    comments = "version: 1.5.5.Final, compiler: javac, environment: Java 21.0.2 (Oracle Corporation)"
)
public class SpecialistMapperImpl implements SpecialistMapper {

    @Override
    public SpecialistDTO toDto(Specialist specialist) {
        if ( specialist == null ) {
            return null;
        }

        SpecialistDTO specialistDTO = new SpecialistDTO();

        if ( specialist.getTeam() != null ) {
            specialistDTO.setTeamId( mapTeamIdToString( specialist.getTeam() ) );
        }
        List<String> list = mapWorkPlanListToStringList( specialist.getWorkPlans() );
        if ( list != null ) {
            specialistDTO.setWorkPlanIds( list );
        }
        if ( specialist.getSpecialistId() != null ) {
            specialistDTO.setSpecialistId( specialist.getSpecialistId().toString() );
        }
        if ( specialist.getName() != null ) {
            specialistDTO.setName( specialist.getName() );
        }
        if ( specialist.getSpecialization() != null ) {
            specialistDTO.setSpecialization( specialist.getSpecialization() );
        }

        return specialistDTO;
    }

    @Override
    public Specialist toEntity(SpecialistDTO specialistDTO) {
        if ( specialistDTO == null ) {
            return null;
        }

        Specialist specialist = new Specialist();

        if ( specialistDTO.getTeamId() != null ) {
            specialist.setTeam( mapStringToTeam( specialistDTO.getTeamId() ) );
        }
        List<WorkPlan> list = mapStringListToWorkPlanList( specialistDTO.getWorkPlanIds() );
        if ( list != null ) {
            specialist.setWorkPlans( list );
        }
        if ( specialistDTO.getSpecialistId() != null ) {
            specialist.setSpecialistId( UUID.fromString( specialistDTO.getSpecialistId() ) );
        }
        if ( specialistDTO.getName() != null ) {
            specialist.setName( specialistDTO.getName() );
        }
        if ( specialistDTO.getSpecialization() != null ) {
            specialist.setSpecialization( specialistDTO.getSpecialization() );
        }

        return specialist;
    }
}
