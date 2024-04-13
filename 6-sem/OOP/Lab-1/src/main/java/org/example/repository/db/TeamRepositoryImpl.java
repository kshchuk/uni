package org.example.repository.db;

import org.apache.log4j.Logger;
import org.example.dao.SpecialistDao;
import org.example.dao.TeamDao;
import org.example.dao.WorkPlanDao;
import org.example.entity.*;
import org.example.repository.TeamRepository;

import java.util.List;
import java.util.UUID;

public class TeamRepositoryImpl implements TeamRepository {
    private Logger logger = Logger.getLogger(TeamRepositoryImpl.class);
    private TeamDao teamDao;
    private SpecialistDao specialistDao;
    private WorkPlanDao workPlanDao;

    public TeamRepositoryImpl(TeamDao teamDao, SpecialistDao specialistDao, WorkPlanDao workPlanDao) {
        this.teamDao = teamDao;
        this.specialistDao = specialistDao;
        this.workPlanDao = workPlanDao;
    }

    @Override
    public void create(Team entity) {
        try {
            teamDao.create(entity);
            for (Specialist specialist : entity.getSpecialists()) {
                var dbSpecialist = specialistDao.read(specialist.getId());
                if (dbSpecialist == null) {
                    specialistDao.create(specialist);
                } else if (!dbSpecialist.equals(specialist)) {
                    specialistDao.update(specialist);
                }
            }
            for (WorkPlan workPlan : entity.getWorkPlans()) {
                var dbWorkPlan = workPlanDao.read(workPlan.getId());
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
            var dbDispatcher = specialistDao.read(entity.getDispatcher().getId());
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
            var dbSpecialists = specialistDao.findByTeamId(entity.getId());
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
            var dbWorkPlans = workPlanDao.findByTeamId(entity.getId());
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
                var dbSpecialist = specialistDao.read(specialist.getId());
                if (dbSpecialist == null) {
                    specialistDao.create(specialist);
                } else if (!dbSpecialist.equals(specialist)) {
                    specialistDao.update(specialist);
                }
            }
            // remove specialists that are not in the updated entity
            List<Specialist> dbSpecialists = specialistDao.findByTeamId(entity.getId());
            for (Specialist dbSpecialist : dbSpecialists) {
                if (!entity.getSpecialists().contains(dbSpecialist)) {
                    specialistDao.delete(dbSpecialist.getId());
                }
            }

            if (entity.getWorkPlans() == null) {
                return;
            }
            for (WorkPlan workPlan : entity.getWorkPlans()) {
                var dbWorkPlan = workPlanDao.read(workPlan.getId());
                if (dbWorkPlan == null) {
                    workPlanDao.create(workPlan);
                } else if (!dbWorkPlan.equals(workPlan)) {
                    workPlanDao.update(workPlan);
                }
            }

            // remove work plans that are not in the updated entity
            List<WorkPlan> dbWorkPlans = workPlanDao.findByTeamId(entity.getId());
            for (WorkPlan dbWorkPlan : dbWorkPlans) {
                if (!entity.getWorkPlans().contains(dbWorkPlan)) {
                    workPlanDao.delete(dbWorkPlan.getId());
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
