package org.example.servlet;

import com.fasterxml.jackson.databind.ObjectMapper;
import org.example.dto.SpecialistDTO;
import org.example.dto.WorkPlanDTO;
import org.example.entity.Specialist;
import org.example.entity.WorkPlan;
import org.example.mapper.SpecialistMapper;
import org.example.mapper.WorkPlanMapper;
import org.example.repository.SpecialistRepository;
import org.example.repository.impl.SpecialistRepositoryImpl;
import org.example.service.SpecialistService;
import org.example.service.impl.SpecialistServiceImpl;

import javax.servlet.annotation.WebServlet;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import java.io.IOException;
import java.io.PrintWriter;
import java.util.List;
import java.util.UUID;
import java.util.logging.Logger;

@WebServlet(name = "specialistServlet", value = "/specialist/*")
public class SpecialistServlet extends HttpServlet {
    Logger logger = Logger.getLogger(SpecialistServlet.class.getName());
    ObjectMapper objectMapper = new ObjectMapper();
    private SpecialistService specialistService;

    public void init() {
        SpecialistRepository specialistRepository = new SpecialistRepositoryImpl();
        specialistService = new SpecialistServiceImpl(specialistRepository);
    }

    public void doGet(HttpServletRequest request, HttpServletResponse response) throws IOException {
        response.setContentType("application/json");
        PrintWriter out = response.getWriter();

        logger.info("GET request to SpecialistServlet" + request.getPathInfo());

        String pathInfo = request.getPathInfo();
        if (pathInfo != null) {
            // Handle the case for "GET /specialist/all"
            if (pathInfo.equals("/all")) {
                List<Specialist> specialists = specialistService.getAll();
                List<SpecialistDTO> specialistDTOs = specialists.stream()
                        .map(SpecialistMapper.INSTANCE::toDto)
                        .toList();

                String jsonResponse = objectMapper.writeValueAsString(specialists);
                out.write(jsonResponse);

                response.setStatus(HttpServletResponse.SC_OK);
            }

            // Handle the case for GET /specialist/workplans?id=...
            else if (pathInfo.startsWith("/workplans")) {
                String id = request.getParameter("id");

                if (id == null) {
                    response.setStatus(HttpServletResponse.SC_BAD_REQUEST);
                    return;
                }

                Specialist specialist = specialistService.get(UUID.fromString(id));
                if (specialist == null) {
                    response.setStatus(HttpServletResponse.SC_NOT_FOUND);
                    return;
                }

                List<WorkPlan> workPlans = specialistService.getWorkPlans(UUID.fromString(id));
                List<WorkPlanDTO> workPlanDTOs = workPlans.stream()
                        .map(WorkPlanMapper.INSTANCE::toDto)
                        .toList();
                String jsonResponse = objectMapper.writeValueAsString(workPlanDTOs);
                out.write(jsonResponse);

                response.setStatus(HttpServletResponse.SC_OK);
            }

            // Handle the case for GET /specialist?id=...
            else {
                String id = request.getParameter("id");
                Specialist specialist = specialistService.get(UUID.fromString(id));

                if (specialist == null) {
                    response.setStatus(HttpServletResponse.SC_NOT_FOUND);
                    return;
                }

                SpecialistDTO specialistDTO = SpecialistMapper.INSTANCE.toDto(specialist);
                String jsonResponse = objectMapper.writeValueAsString(specialistDTO);
                out.write(jsonResponse);

                response.setStatus(HttpServletResponse.SC_OK);
            }
        }
        else {
            response.setStatus(HttpServletResponse.SC_BAD_REQUEST);
        }
    }


    public void doPost(HttpServletRequest request, HttpServletResponse response) throws IOException {
        response.setContentType("application/json");
        String body = request.getReader().lines().reduce("", (accumulator, actual) -> accumulator + actual);

        logger.info("POST request to SpecialistServlet" + body);

        if (body.isEmpty()) {
            response.setStatus(HttpServletResponse.SC_BAD_REQUEST);
            return;
        }

        SpecialistDTO specialistDTO;
        try {
            specialistDTO = objectMapper.readValue(body, SpecialistDTO.class);
        } catch (Exception e) {
            response.setStatus(HttpServletResponse.SC_BAD_REQUEST);
            return;
        }
        Specialist specialist = SpecialistMapper.INSTANCE.toEntity(specialistDTO);
        specialistService.create(specialist);

        response.setStatus(HttpServletResponse.SC_CREATED);
    }

    public void doDelete(HttpServletRequest request, HttpServletResponse response) throws IOException {
        response.setContentType("application/json");
        String pathInfo = request.getPathInfo();

        logger.info("DELETE request to SpecialistServlet" + pathInfo);

        if (pathInfo != null) {
                String id = request.getParameter("id");
                if (id == null) {
                    response.setStatus(HttpServletResponse.SC_BAD_REQUEST);
                    return;
                }

                boolean isDeleted = specialistService.delete(UUID.fromString(id));
                if (isDeleted) {
                    response.setStatus(HttpServletResponse.SC_OK);
                } else {
                    response.setStatus(HttpServletResponse.SC_NOT_FOUND);
                }
        }
        else {
            response.setStatus(HttpServletResponse.SC_BAD_REQUEST);
        }
    }

    public void doPut(HttpServletRequest request, HttpServletResponse response) throws IOException {
        response.setContentType("application/json");
        String body = request.getReader().lines().reduce("", (accumulator, actual) -> accumulator + actual);

        logger.info("PUT request to SpecialistServlet" + body);

        if (body.isEmpty()) {
            response.setStatus(HttpServletResponse.SC_BAD_REQUEST);
            return;
        }

        SpecialistDTO specialistDTO;
        try {
            specialistDTO = objectMapper.readValue(body, SpecialistDTO.class);
        } catch (Exception e) {
            response.setStatus(HttpServletResponse.SC_BAD_REQUEST);
            return;
        }

        Specialist specialist = SpecialistMapper.INSTANCE.toEntity(specialistDTO);
        Specialist oldSpecialist = specialistService.get(UUID.fromString(specialistDTO.getSpecialistId()));
        if (oldSpecialist == null) {
            specialistService.create(specialist);
            response.setStatus(HttpServletResponse.SC_CREATED);
        } else {
            specialistService.update(specialist);
            response.setStatus(HttpServletResponse.SC_OK);
        }
    }

    public void destroy() {
    }
}
