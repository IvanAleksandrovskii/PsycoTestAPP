# core/models/send_test.py

"""
TODO: Idea - to make possible for one user to send tests to other users. For example, if I want to send tests to someone
I will press the button and will get a question to send the username of the user to whom I want to send tests.
After that I will recive the list of all availible active tests and will choose so much as I want.
After that I will recive a message to confirm sending the tests withe the username of the user to whom I want to send tests.

Then I will recive the message if the user got the tests delivered to him or not. If not I will say that he didn't get it 
because he didn't activated the bot and will try to send the tests again later. Since that moment bot should check if someone 
started the bot and he has tests for him not completed. After success delivery sender should get a message that tests was delivered.
After that user (receiver) should press the button inside his message to start tests. He will get a list of all tests send to him with 
the complete status. After he finnish test his test result saves to the database and the test marks as completed.
After user done all his tests he and got all results separate, his result saves to the database where information about all tests 
was send information is kept. 
"""

# Обновленный план реализации:
# 1. Создать новую модель в базе данных для хранения информации об отправленных тестах и листе ожидания
# 2. Обновить логику отправки тестов с учетом листа ожидания
# 3. Обновить обработчик команды /start для проверки наличия неотвеченных тестов и тестов из листа ожидания
# 4. Добавить уведомления для отправителей тестов

from sqlalchemy import Column, ForeignKey, Boolean, DateTime, String, BigInteger
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from core.models.base import Base
# from handlers.psyco_tests import start_test

class SentTest(Base):
    __tablename__ = "sent_tests"

    # sender_id = Column(UUID(as_uuid=True), ForeignKey("tg_users.id"), nullable=False)
    # sender = relationship("TGUser", foreign_keys=[sender_id])

    sender_id = Column(BigInteger, nullable=False)

    test_id = Column(UUID(as_uuid=True), ForeignKey("psyco_tests.id"), nullable=False)
    test = relationship("PsycoTest")

    # receiver_id = Column(UUID(as_uuid=True), ForeignKey("tg_users.id"), nullable=True)
    # receiver = relationship("TGUser", foreign_keys=[receiver_id])

    receiver_id = Column(BigInteger, nullable=True)

    receiver_username = Column(String, nullable=False)

    is_completed = Column(Boolean, default=False)  # TODO: Make it working
    is_delivered = Column(Boolean, default=False)  # TODO: Make it working
    # sent_at = Column(DateTime(timezone=True), server_default=func.now())
    delivered_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
