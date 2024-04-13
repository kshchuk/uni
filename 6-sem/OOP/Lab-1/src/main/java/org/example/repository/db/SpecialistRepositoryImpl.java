package org.example.repository.db;

import org.apache.log4j.Logger;
import org.example.dao.SpecialistDao;
import org.example.dao.TeamDao;
import org.example.dao.WorkPlanDao;
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

    public SpecialistRepositoryImpl(SpecialistDao specialistDao, TeamDao teamDao, WorkPlanDao workPlanDao) {
        this.specialistDao = specialistDao;
        this.teamDao = teamDao;
        this.workPlanDao = workPlanDao;
    }

    @Override
    public void create(Specialist entity) {
        try {
            specialistDao.create(entity);
            if (entity.getTeam() != null) {
                var dbTeam = teamDao.read(entity.getTeam().getId());
                if (dbTeam == null) {
                    teamDao.create(entity.getTeam());
                } else if (!dbTeam.equals(entity.getTeam())) {
                    teamDao.update(entity.getTeam());
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
            var team = teamDao.read(entity.getTeam().getId());
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
            if (entity.getTeam() != null) {
                var dbTeam = teamDao.read(entity.getTeam().getId());
                if (dbTeam == null) {
                    teamDao.create(entity.getTeam());
                } else if (!dbTeam.equals(entity.getTeam())) {
                    teamDao.update(entity.getTeam());
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
