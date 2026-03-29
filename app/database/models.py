from datetime import datetime
from sqlalchemy import Integer, Float, String, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.orm import relationship, DeclarativeBase, mapped_column, Mapped
from typing import List, Optional


class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = 'user'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, unique=True, nullable=False)
    login: Mapped[Optional[str]] = mapped_column(String, unique=True, nullable=True)
    password_hash: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    access_token: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    materials: Mapped[List["Material"]] = relationship("Material", back_populates='user',
                                                       cascade="all, delete-orphan")
    school_services: Mapped[List["SchoolService"]] = relationship("SchoolService", back_populates='user',
                                                                  cascade="all, delete-orphan")
    admin: Mapped[Optional["Admin"]] = relationship("Admin", back_populates="user", uselist=False)
    bonuses: Mapped[List["Bonus"]] = relationship("Bonus", back_populates="user")
    social_networks: Mapped[List["SocialNetwork"]] = relationship("SocialNetwork", back_populates="user")


class Material(Base):
    __tablename__ = 'materials'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String, nullable=False)
    file_url: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('user.user_id', ondelete='CASCADE'), nullable=False)

    user = relationship("User", back_populates="materials")


class Admin(Base):
    __tablename__ = 'admin'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('user.id'), unique=True, nullable=False)
    role: Mapped[str] = mapped_column(String, default='admin')

    user: Mapped["User"] = relationship('User', back_populates='admin')


class SchoolService(Base):
    __tablename__ = 'school_services'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    price: Mapped[float] = mapped_column(Float, nullable=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('user.user_id', ondelete='CASCADE'), nullable=False)

    user: Mapped["User"] = relationship("User", back_populates="school_services")


class Bonus(Base):
    __tablename__ = "bonuses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String, nullable=False)  # Короткое название бонуса
    description: Mapped[str] = mapped_column(Text, nullable=False)  # Что это за бонус
    action_text: Mapped[str] = mapped_column(Text, nullable=False)  # Что нужно сделать, чтобы его получить
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('user.user_id', ondelete='CASCADE'), nullable=False)
    user: Mapped["User"] = relationship("User", back_populates="bonuses")


class SocialNetwork(Base):
    __tablename__ = "social_networks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    platform: Mapped[str] = mapped_column(String, nullable=False)
    url: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    phone: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('user.user_id', ondelete="CASCADE"), nullable=False)
    user: Mapped["User"] = relationship("User", back_populates="social_networks")


# class Teacher(Base):
#     __tablename__ = 'teacher'
#
#     id: Mapped[int] = mapped_column(Integer, primary_key=True)
#     user_id: Mapped[int] = mapped_column(Integer, ForeignKey('user.id'), unique=True, nullable=False)
#     qualification: Mapped[Optional[str]] = mapped_column(String, nullable=True)
#     bio: Mapped[Optional[str]] = mapped_column(String, nullable=True)
#
#     user: Mapped["User"] = relationship('User', back_populates='teacher')
    # lessons: Mapped[List["Lesson"]] = relationship('Lesson', back_populates='teacher')


# class Lesson(Base):
#     __tablename__ = 'lesson'
#
#     id: Mapped[int] = mapped_column(Integer, primary_key=True)
#     title: Mapped[str] = mapped_column(String)
#     date: Mapped[datetime] = mapped_column(DateTime)
#     max_students: Mapped[int] = mapped_column(Integer)
#     created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
#     teacher_id: Mapped[int] = mapped_column(Integer, ForeignKey('teacher.id'))
#
#     teacher: Mapped[Optional["Teacher"]] = relationship('Teacher', back_populates='lessons')
#     materials: Mapped[List["Materials"]] = relationship('Materials', back_populates='lesson')
#     enrollments: Mapped[List["Enrollments"]] = relationship('Enrollments', back_populates='lesson')
#     progress: Mapped[List["Progress"]] = relationship("Progress", back_populates="lesson")


# class Enrollments(Base):
#     __tablename__ = 'enrollments'
#
#     id: Mapped[int] = mapped_column(Integer, primary_key=True)
#     user_id: Mapped[int] = mapped_column(Integer, ForeignKey('user.id'), nullable=False)
#     registered_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
#
#     lesson: Mapped["Lesson"] = relationship('Lesson', back_populates='enrollments')
#     user: Mapped["User"] = relationship('User', back_populates='enrollments')


# class Progress(Base):
#     __tablename__ = 'progress'
#
#     id: Mapped[int] = mapped_column(Integer, primary_key=True)
#     user_id: Mapped[int] = mapped_column(Integer, ForeignKey('user.id'), nullable=False)
#     lesson_id: Mapped[int] = mapped_column(Integer, ForeignKey('lesson.id'), nullable=False)
#     progress: Mapped[float] = mapped_column(Float, default=0.0)  # Прогресс от 0.0 до 100.0
#     updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
#
#     user: Mapped["User"] = relationship("User", back_populates="progress")
#     lesson: Mapped["Lesson"] = relationship("Lesson", back_populates="progress")
