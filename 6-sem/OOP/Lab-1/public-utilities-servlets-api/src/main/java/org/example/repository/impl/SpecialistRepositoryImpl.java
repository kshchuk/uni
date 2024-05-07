package org.example.repository.impl;

import org.apache.log4j.Logger;
import org.example.dao.SpecialistDao;
import org.example.dao.TeamDao;
import org.example.dao.WorkPlanDao;
import org.example.dao.db.DAOManager;
import org.example.entity.Specialist;
import org.example.entity.WorkPlan;
import org.example.repository.SpecialistRepository;

import java.util.List;
import java.util.UUID;

public class SpecialistRepositoryImpl implements SpecialistRepository {
    private Logger logger = Logger.getLogger(SpecialistRepositoryImpl.class);
    private SpecialistDao specialistDao;
    private TeamDao teamDao;
    private WorkPlanDao workPlanDao;

    public SpecialistRepositoryImpl() {
        DAOManager manager = DAOManager.getInstance();
        try {
            specialistDao = (SpecialistDao) manager.getDAO(DAOManager.Table.SPECIALIST);
            teamDao = (TeamDao) manager.getDAO(DAOManager.Table.TEAM);
            workPlanDao = (WorkPlanDao) manager.getDAO(DAOManager.Table.WORKPLAN);
        } catch (Exception e) {
            logger.error(e);
        }
    }

    @Override
    public void create(Specialist entity) {
        try {
            specialistDao.create(entity);
        } catch (Exception e) {
            logger.error(e);
        }
    }

    @Override
    public Specialist read(UUID uuid) {
        try {
            return specialistDao.read(uuid);
        } catch (Exception e) {
            logger.error(e);
            return null;
        }
    }

    @Override
    public Specialist readWithTeam(Specialist entity) {
        try {
            var team = teamDao.read(entity.getTeam().getTeamId());
            entity.setTeam(team);
            return entity;
        } catch (Exception e) {
            logger.error(e);
            return null;
        }
    }

    @Override
    public Specialist readWithWorkPlans(Specialist entity) {
        try {
            var workPlans = workPlanDao.findByDispatcherId(entity.getSpecialistId());
            entity.setWorkPlans(workPlans);
            return entity;
        } catch (Exception e) {
            logger.error(e);
            return null;
        }
    }

    @Override
    public void update(Specialist entity) {
        try {
            specialistDao.update(entity);
        } catch (Exception e) {
            logger.error(e);
        }
    }

    @Override
    public void delete(UUID uuid) {
        try {
            specialistDao.delete(uuid);
        } catch (Exception e) {
            logger.error(e);
        }
    }

    @Override
    public List<Specialist> findAll() {
        try {
            return specialistDao.findAll();
        } catch (Exception e) {
            logger.error(e);
            return null;
        }
    }
}
