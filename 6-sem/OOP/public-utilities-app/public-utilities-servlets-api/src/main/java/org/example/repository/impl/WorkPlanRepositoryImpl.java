package org.example.repository.impl;

import org.apache.log4j.Logger;
import org.example.dao.TeamDao;
import org.example.dao.WorkPlanDao;
import org.example.dao.db.DAOManager;
import org.example.entity.WorkPlan;
import org.example.repository.WorkPlanRepository;

import java.util.List;
import java.util.UUID;

public class WorkPlanRepositoryImpl implements WorkPlanRepository {
    private Logger logger = Logger.getLogger(WorkPlanRepositoryImpl.class);
    private WorkPlanDao workPlanDao;
    private TeamDao teamDao;

    public WorkPlanRepositoryImpl() {
        DAOManager manager = DAOManager.getInstance();
        try {
            workPlanDao = (WorkPlanDao) manager.getDAO(DAOManager.Table.WORKPLAN);
            teamDao = (TeamDao) manager.getDAO(DAOManager.Table.TEAM);
        } catch (Exception e) {
            logger.error(e);
        }
    }

    @Override
    public void create(WorkPlan entity) {
        try {
            workPlanDao.create(entity);
        } catch (Exception e) {
            logger.error(e);
        }
    }

    @Override
    public WorkPlan read(UUID uuid) {
        try {
            WorkPlan workPlan = workPlanDao.read(uuid);
            var team = teamDao.read(workPlan.getTeam().getTeamId());
            workPlan.setTeam(team);
            return workPlan;
        } catch (Exception e) {
            logger.error(e);
            return null;
        }
    }

    @Override
    public WorkPlan readWithTeam(WorkPlan workPlan) {
        try {
            var team = teamDao.read(workPlan.getTeam().getTeamId());
            workPlan.setTeam(team);
            return workPlan;
        } catch (Exception e) {
            logger.error(e);
            return null;
        }
    }

    @Override
    public void update(WorkPlan entity) {
        try {
            workPlanDao.update(entity);
        } catch (Exception e) {
            logger.error(e);
        }
    }

    @Override
    public void delete(UUID uuid) {
        try {
            workPlanDao.delete(uuid);
        } catch (Exception e) {
            logger.error(e);
        }
    }

    @Override
    public List<WorkPlan> findAll() {
        try {
            List<WorkPlan> workPlans = workPlanDao.findAll();
            for (WorkPlan workPlan : workPlans) {
                var team = teamDao.read(workPlan.getTeam().getTeamId());
                workPlan.setTeam(team);
            }
            return workPlans;
        } catch (Exception e) {
            logger.error(e);
            return null;
        }
    }
}
