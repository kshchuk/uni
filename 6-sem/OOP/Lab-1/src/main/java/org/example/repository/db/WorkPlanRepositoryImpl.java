package org.example.repository.db;

import org.apache.log4j.Logger;
import org.example.dao.TeamDao;
import org.example.dao.WorkPlanDao;
import org.example.entity.WorkPlan;
import org.example.repository.WorkPlanRepository;

import java.util.List;
import java.util.UUID;

public class WorkPlanRepositoryImpl implements WorkPlanRepository {
    private Logger logger = Logger.getLogger(WorkPlanRepositoryImpl.class);
    private WorkPlanDao workPlanDao;
    private TeamDao teamDao;

    public WorkPlanRepositoryImpl(WorkPlanDao workPlanDao, TeamDao teamDao) {
        this.workPlanDao = workPlanDao;
        this.teamDao = teamDao;
    }

    @Override
    public void create(WorkPlan entity) {
        try {
            workPlanDao.create(entity);
            if (entity.getTeam() != null) {
                var dbTeam = teamDao.read(entity.getTeam().getTeamId());
                if (dbTeam == null) {
                    teamDao.create(entity.getTeam());
                } else if (!dbTeam.equals(entity.getTeam())) {
                    teamDao.update(entity.getTeam());
                }
            }
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
            if (entity.getTeam() == null) {
                return;
            }
            var dbTeam = teamDao.read(entity.getTeam().getTeamId());
            if (dbTeam == null) {
                teamDao.create(entity.getTeam());
            } else if (!dbTeam.equals(entity.getTeam())) {
                teamDao.update(entity.getTeam());
            }
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
