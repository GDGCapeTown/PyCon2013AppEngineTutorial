import endpoints
from protorpc import messages
from protorpc import message_types
from protorpc import remote

import schema

package = 'AskTheUniverseAQuestion'

WEB_CLIENT_ID = '394729362556.apps.googleusercontent.com'
ANDROID_CLIENT_ID = '394729362556-qnsuj4icghoa5q8cnpu7jqarm5j9omlp.apps.googleusercontent.com'
ANDROID_AUDIENCE = WEB_CLIENT_ID


class Question(messages.Message):
    id = messages.IntegerField(1)
    question = messages.StringField(2)
    day = messages.IntegerField(3)
    month = messages.IntegerField(4)
    year = messages.IntegerField(5)

class QuestionCollection(messages.Message):
    items = messages.MessageField(Question, 1, repeated=True)

@endpoints.api(name='questionService', version='v1',description='Allows users to ask questions from remote apps',
                allowed_client_ids=[WEB_CLIENT_ID, ANDROID_CLIENT_ID,endpoints.API_EXPLORER_CLIENT_ID],
                audiences=[ANDROID_AUDIENCE],
                scopes=[endpoints.EMAIL_SCOPE])
class AskTheUniverseService(remote.Service):

    MULTIPLY_METHOD_RESOURCE = endpoints.ResourceContainer(question=messages.StringField(1, variant=messages.Variant.STRING,required=True))

    @endpoints.method(MULTIPLY_METHOD_RESOURCE, Question,path='questionServiceQuestion', http_method='POST',name='questionService.askQuestion')
    def questionService_question(self, request):

        user_obj = endpoints.get_current_user()
        if user_obj is None:

            # Error !
            raise endpoints.UnauthorizedException('Invalid token.')

        else:

            # Setup our model
            question_obj = schema.UniverseQuestion()
            question_obj.created_by = user_obj
            question_obj.message = request.question
            question_obj.put()

            return Question(

                id=int(question_obj.key.id()),
                question=question_obj.message,
                day=int(question_obj.created.day),
                month=int(question_obj.created.month),
                year=int(question_obj.created.year)

            )

    ANSWER_METHOD_RESOURCE = endpoints.ResourceContainer(id=messages.IntegerField(1, variant=messages.Variant.UINT64,required=True),answer=messages.StringField(2, variant=messages.Variant.STRING,required=True))
    @endpoints.method(ANSWER_METHOD_RESOURCE, Question,path='questionServiceAnswer', http_method='POST',name='questionService.sendAnswer')
    def questionService_answer(self, request):

        user_obj = endpoints.get_current_user()
        if user_obj is None:

            # Error !
            raise endpoints.UnauthorizedException('Invalid token.')

        else:

            # Get the question
            question_obj = schema.UniverseQuestion.get_by_id( long(request.id) )

            # Did we find it
            if question_obj != None:

                # Not already answered ???
                if question_obj.answer != None:

                    raise endpoints.ForbiddenException('Question already has a answer find your own claim to fame !')

                else:

                    # Setup our model
                    question_obj.answer = request.answer
                    question_obj.answer_by = user_obj

                    # Save
                    question_obj.put()

                    # Return
                    return Question(

                        id=int(question_obj.key.id()),
                        question=question_obj.message,
                        day=int(question_obj.created.day),
                        month=int(question_obj.created.month),
                        year=int(question_obj.created.year)

                    )

            else: raise endpoints.NotFoundException('No such Question')

    @endpoints.method(message_types.VoidMessage, QuestionCollection,
                      path='questionServiceList', http_method='GET',
                      name='questionService.getAllQuestions')
    def questionService_list(self, unused_request):

        user_obj = endpoints.get_current_user()
        if user_obj is None:

            # Error !
            raise endpoints.UnauthorizedException('Invalid token.')

        else:

            # Get the questions for the user
            question_objs = schema.UniverseQuestion.get_current_questions(user_obj)

            # Public objs
            public_question_objs = []

            # Loop and add each
            for question_obj in question_objs:

                # Add it
                public_question_objs.append( Question(

                    id=int(question_obj.key.id()),
                    question=question_obj.message,
                    day=int(question_obj.created.day),
                    month=int(question_obj.created.month),
                    year=int(question_obj.created.year)

                ) )

            # Output questions
            return QuestionCollection(items=public_question_objs)

app = endpoints.api_server([AskTheUniverseService], restricted=False)
