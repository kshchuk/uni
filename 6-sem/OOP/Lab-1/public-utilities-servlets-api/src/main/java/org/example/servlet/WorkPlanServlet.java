package org.example.servlet;

import com.fasterxml.jackson.databind.ObjectMapper;
import org.example.dto.WorkPlanDTO;
import org.example.entity.WorkPlan;
import org.example.mapper.WorkPlanMapper;
import org.example.repository.WorkPlanRepository;
import org.example.repository.impl.WorkPlanRepositoryImpl;
import org.example.service.WorkPlanService;
import org.example.service.impl.WorkPlanServiceImpl;

import javax.servlet.annotation.WebServlet;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import java.io.IOException;
import java.io.PrintWriter;
import java.util.List;
import java.util.UUID;
import java.util.logging.Logger;

@WebServlet(name = "WorkPlanServlet", value = "/work-plan/*")
public class WorkPlanServlet extends HttpServlet {
    Logger logger = Logger.getLogger(SpecialistServlet.class.getName());
    ObjectMapper objectMapper = new ObjectMapper();
    private WorkPlanService workPlanService;

    public void init() {
        WorkPlanRepository workPlanRepository = new WorkPlanRepositoryImpl();
        workPlanService = new WorkPlanServiceImpl(workPlanRepository);
    }

    public void doGet(HttpServletRequest request, HttpServletResponse response) throws IOException, IOException {
        response.setHeader("Access-Control-Allow-Origin", "http://localhost:3000");
        response.setHeader("Access-Control-Allow-Methods", "GET");
        response.setHeader("Access-Control-Allow-Headers", "Content-Type");
        response.setHeader("Access-Control-Max-Age", "3600");
        response.setContentType("application/json");
        PrintWriter out = response.getWriter();

        logger.info("GET request to WorkPlanServlet" + request.getPathInfo());

        String pathInfo = request.getPathInfo();
        if (pathInfo != null) {
            // Handle the case for "GET /work-plan/all"
            if (pathInfo.equals("/all")) {
                List<WorkPlan> workPlans = workPlanService.getAll();

                List<WorkPlanDTO> workPlanDTOs = workPlans.stream()
                        .map(WorkPlanMapper.INSTANCE::toDto)
                        .toList();

                String jsonResponse = objectMapper.writeValueAsString(workPlanDTOs);
                out.write(jsonResponse);

                response.setStatus(HttpServletResponse.SC_OK);
            }

            // Handle the case for GET /work-plan?id=...
            else {
                String id = request.getParameter("id");

                if (id == null) {
                    response.setStatus(HttpServletResponse.SC_BAD_REQUEST);
                    return;
                }

                WorkPlan workPlan = workPlanService.get(UUID.fromString(id));

                if (workPlan == null) {
                    response.setStatus(HttpServletResponse.SC_NOT_FOUND);
                    return;
                }

                WorkPlanDTO workPlanDTO = WorkPlanMapper.INSTANCE.toDto(workPlan);

                String jsonResponse = objectMapper.writeValueAsString(workPlanDTO);
                out.write(jsonResponse);

                response.setStatus(HttpServletResponse.SC_OK);
            }
        } else {
            response.setStatus(HttpServletResponse.SC_BAD_REQUEST);
        }
    }

    public void doPost(HttpServletRequest request, HttpServletResponse response) throws IOException {
        response.setHeader("Access-Control-Allow-Origin", "http://localhost:3000");
        response.setHeader("Access-Control-Allow-Methods", "GET");
        response.setHeader("Access-Control-Allow-Headers", "Content-Type");
        response.setHeader("Access-Control-Max-Age", "3600");
        response.setContentType("application/json");
        String body = request.getReader().lines().reduce("", (accumulator, actual) -> accumulator + actual);


        logger.info("POST request to WorkPlanServlet" + request.getPathInfo());

        if (body.isEmpty()) {
            response.setStatus(HttpServletResponse.SC_BAD_REQUEST);
            return;
        }

        WorkPlanDTO workPlanDTO;
        try {
            workPlanDTO = objectMapper.readValue(request.getReader(), WorkPlanDTO.class);
        } catch (Exception e) {
            response.setStatus(HttpServletResponse.SC_BAD_REQUEST);
            return;
        }
        WorkPlan workPlan = WorkPlanMapper.INSTANCE.toEntity(workPlanDTO);
        workPlanService.create(workPlan);

        response.setStatus(HttpServletResponse.SC_CREATED);
    }

    public void doDelete(HttpServletRequest request, HttpServletResponse response) throws IOException {
        response.setHeader("Access-Control-Allow-Origin", "http://localhost:3000");
        response.setHeader("Access-Control-Allow-Methods", "GET");
        response.setHeader("Access-Control-Allow-Headers", "Content-Type");
        response.setHeader("Access-Control-Max-Age", "3600");
        response.setContentType("application/json");
        String pathInfo = request.getPathInfo();

        logger.info("DELETE request to WorkPlanServlet" + request.getPathInfo());

        if (pathInfo != null) {
            String id = request.getParameter("id");

            if (id == null) {
                response.setStatus(HttpServletResponse.SC_BAD_REQUEST);
                return;
            }

            boolean isDeleted = workPlanService.delete(UUID.fromString(id));
            if (isDeleted) {
                response.setStatus(HttpServletResponse.SC_OK);
            } else {
                response.setStatus(HttpServletResponse.SC_NOT_FOUND);
            }

        } else {
            response.setStatus(HttpServletResponse.SC_BAD_REQUEST);
        }
    }

    public void doPut(HttpServletRequest request, HttpServletResponse response) throws IOException {
        response.setHeader("Access-Control-Allow-Origin", "http://localhost:3000");
        response.setHeader("Access-Control-Allow-Methods", "GET");
        response.setHeader("Access-Control-Allow-Headers", "Content-Type");
        response.setHeader("Access-Control-Max-Age", "3600");
        response.setContentType("application/json");
        String body = request.getReader().lines().reduce("", (accumulator, actual) -> accumulator + actual);

        logger.info("PUT request to WorkPlanServlet" + request.getPathInfo());

        if (body.isEmpty()) {
            response.setStatus(HttpServletResponse.SC_BAD_REQUEST);
            return;
        }

        WorkPlanDTO workPlanDTO;
        try {
            workPlanDTO = objectMapper.readValue(body, WorkPlanDTO.class);
        } catch (Exception e) {
            response.setStatus(HttpServletResponse.SC_BAD_REQUEST);
            return;
        }

        WorkPlan workPlan = WorkPlanMapper.INSTANCE.toEntity(workPlanDTO);
        WorkPlan oldWorkPlan = workPlanService.get(UUID.fromString(workPlanDTO.getWorkPlanId()));
        if (oldWorkPlan == null) {
            workPlanService.create(workPlan);
            response.setStatus(HttpServletResponse.SC_CREATED);
        } else {
            workPlanService.update(workPlan);
            response.setStatus(HttpServletResponse.SC_OK);
        }
    }
}
