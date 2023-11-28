class StudentsController < ApplicationController
  skip_before_action :verify_authenticity_token
  layout 'application'
  def index
    @students = Student.all
  end

  def new
    @student = Student.new
  end

  def create
    @student = Student.new(student_params)
    if @student.save
      redirect_to '/'
    else
      render '/new'
    end
  end

  def show
    puts "show"
    @student = Student.find(params[:id])
  end

  def edit
    @student = Student.find(params[:id])
  end

  def update
    @student = Student.find(params[:id])
    if @student.update(student_params)
      redirect_to student_path(@student)
    else
      render "edit"
    end
  end

  def destroy
    @student = Student.find(params[:id])
    @student.destroy
    redirect_to students_path
  end


  private
  def student_params
    params.require(:student).permit(:name, :age, :dorm, :language, :teacher, :university)
  end


end
