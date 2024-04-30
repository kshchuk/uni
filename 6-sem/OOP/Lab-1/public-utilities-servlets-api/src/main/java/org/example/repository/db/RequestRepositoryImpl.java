package org.example.repository.db;

import org.apache.log4j.Logger;
import org.example.dao.RequestDao;
import org.example.entity.Request;
import org.example.repository.RequestRepository;

import java.util.List;
import java.util.UUID;

public class RequestRepositoryImpl implements RequestRepository {
    private Logger logger = Logger.getLogger(RequestRepositoryImpl.class);
    private RequestDao requestDao;

    public RequestRepositoryImpl(RequestDao requestDao) {
        this.requestDao = requestDao;
    }

    @Override
    public void create(Request entity) {
        try {
            requestDao.create(entity);
        } catch (Exception e) {
            logger.error(e);
        }
    }

    @Override
    public Request read(UUID uuid) {
        try {
            return requestDao.read(uuid);
        } catch (Exception e) {
            logger.error(e);
        }
        return null;
    }

    @Override
    public void update(Request entity) {
        try {
            requestDao.update(entity);
        } catch (Exception e) {
            logger.error(e);
        }
    }

    @Override
    public void delete(UUID uuid) {
        try {
            requestDao.delete(uuid);
        } catch (Exception e) {
            logger.error(e);
        }
    }

    @Override
    public List<Request> findAll() {
        try {
            return requestDao.findAll();
        } catch (Exception e) {
            logger.error(e);
        }
        return null;
    }
}
