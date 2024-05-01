package org.example.repository.impl;

import org.apache.log4j.Logger;
import org.example.dao.SpecialistDao;
import org.example.dao.TeamDao;
import org.example.dao.WorkPlanDao;
import org.example.dao.db.DAOManager;
import org.example.entity.Specialist;
import org.example.entity.Team;
import org.example.entity.WorkPlan;
import org.example.repository.TeamRepository;

import java.util.List;
import java.util.UUID;

public class TeamRepositoryImpl implements TeamRepository {
    private Logger logger = Logger.getLogger(TeamRepositoryImpl.class);
    private TeamDao teamDao;
    private SpecialistDao specialistDao;
    private WorkPlanDao workPlanDao;

    public TeamRepositoryImpl() {
        DAOManager manager = DAOManager.getInstance();
        try {
            teamDao = (TeamDao) manager.getDAO(DAOManager.Table.TEAM);
            specialistDao = (SpecialistDao) manager.getDAO(DAOManager.Table.SPECIALIST);
            workPlanDao = (WorkPlanDao) manager.getDAO(DAOManager.Table.WORKPLAN);
        } catch (Exception e) {
            logger.error(e);
        }
    }

    @Override
    public void create(Team entity) {
        try {
            teamDao.create(entity);
            for (Specialist specialist : entity.getSpecialists()) {
                var dbSpecialist = specialistDao.read(specialist.getSpecialistId());
                if (dbSpecialist == null) {
                    specialistDao.create(specialist);
                } else if (!dbSpecialist.equals(specialist)) {
                    specialistDao.update(specialist);
                }
            }
            for (WorkPlan workPlan : entity.getWorkPlans()) {
                var dbWorkPlan = workPlanDao.read(workPlan.getWorkPlanId());
                if (dbWorkPlan == null) {
                    workPlanDao.create(workPlan);
                } else if (!dbWorkPlan.equals(workPlan)) {
                    workPlanDao.update(workPlan);
                }
            }
        } catch (Exception e) {
            logger.error(e);
        }
    }

    @Override
    public Team read(UUID uuid) {
        try {
            Team team = teamDao.read(uuid);
            return team;
        } catch (Exception e) {
            logger.error(e);
            return null;
        }
    }

    @Override
    public Team readWithDispatcher(Team entity) {
        try {
            var dbDispatcher = specialistDao.read(entity.getDispatcher().getSpecialistId());
            entity.setDispatcher(dbDispatcher);
            return entity;
        } catch (Exception e) {
            logger.error(e);
            return null;
        }
    }

    @Override
    public Team readWithSpecialists(Team entity) {
        try {
            var dbSpecialists = specialistDao.findByTeamId(entity.getTeamId());
            entity.setSpecialists(dbSpecialists);
            return entity;
        } catch (Exception e) {
            logger.error(e);
            return null;
        }
    }

    @Override
    public Team readWithWorkPlans(Team entity) {
        try {
            var dbWorkPlans = workPlanDao.findByTeamId(entity.getTeamId());
            entity.setWorkPlans(dbWorkPlans);
            return entity;
        } catch (Exception e) {
            logger.error(e);
            return null;
        }
    }

    @Override
    public void update(Team entity) {
        try {
            teamDao.update(entity);
            if (entity.getSpecialists() == null) {
                return;
            }
            for (Specialist specialist : entity.getSpecialists()) {
                var dbSpecialist = specialistDao.read(specialist.getSpecialistId());
                if (dbSpecialist == null) {
                    specialistDao.create(specialist);
                } else if (!dbSpecialist.equals(specialist)) {
                    specialistDao.update(specialist);
                }
            }
            // remove specialists that are not in the updated entity
            List<Specialist> dbSpecialists = specialistDao.findByTeamId(entity.getTeamId());
            for (Specialist dbSpecialist : dbSpecialists) {
                if (!entity.getSpecialists().contains(dbSpecialist)) {
                    specialistDao.delete(dbSpecialist.getSpecialistId());
                }
            }

            if (entity.getWorkPlans() == null) {
                return;
            }
            for (WorkPlan workPlan : entity.getWorkPlans()) {
                var dbWorkPlan = workPlanDao.read(workPlan.getWorkPlanId());
                if (dbWorkPlan == null) {
                    workPlanDao.create(workPlan);
                } else if (!dbWorkPlan.equals(workPlan)) {
                    workPlanDao.update(workPlan);
                }
            }

            // remove work plans that are not in the updated entity
            List<WorkPlan> dbWorkPlans = workPlanDao.findByTeamId(entity.getTeamId());
            for (WorkPlan dbWorkPlan : dbWorkPlans) {
                if (!entity.getWorkPlans().contains(dbWorkPlan)) {
                    workPlanDao.delete(dbWorkPlan.getWorkPlanId());
                }
            }
        } catch (Exception e) {
            logger.error(e);
        }
    }

    @Override
    public void delete(UUID uuid) {
        try {
            teamDao.delete(uuid);
        } catch (Exception e) {
            logger.error(e);
        }
    }

    @Override
    public List<Team> findAll() {
        try {
            List<Team> teams = teamDao.findAll();
            return teams;
        } catch (Exception e) {
            logger.error(e);
            return null;
        }
    }
}
