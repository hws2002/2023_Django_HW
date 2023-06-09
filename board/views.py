import json
from django.http import HttpRequest, HttpResponse

from board.models import Board, User
from utils.utils_request import BAD_METHOD, request_failed, request_success, return_field
from utils.utils_require import MAX_CHAR_LENGTH, CheckRequire, require
from utils.utils_time import get_timestamp


def check_for_board_data(body):
    board = require(body, "board", "string", err_msg="Missing or error type of [board]")
    
    # TODO Start: [Student] add checks for type of boardName and userName
    board_name = require(body, "boardName", "string", err_msg="Missing or error type of [boardName]")
    user_name = require(body, "userName", "string", err_msg="Missing or error type of [userName]")
    # TODO End: [Student] add checks for type of boardName and userName
    
    assert 0 < len(board_name) <= 50, "Bad length of [boardName]"
    
    # TODO Start: [Student] add checks for length of userName and board
    assert 0 < len(user_name) <= 50, "Bad length of [userName]"
    assert len(board) == 2500, "Bad length of [board]"
    # TODO End: [Student] add checks for length of userName and board
    
    
    # TODO Start: [Student] and more checks (you should read API docs carefully)
    # checks for char of board, only 0 and 1 is acceptable
    # should throw 400 bad request when not valid
    # assert all(char in ['0', '1'] for char in board), "Invalid char in [board]"
    for char in board:
        assert char == '0' or char == '1', "Invalid char in [board]"
    # TODO End: [Student] and more checks (you should read API docs carefully)
    return board, board_name, user_name


@CheckRequire
def startup(req: HttpRequest):
    return HttpResponse("Congratulations! You have successfully installed the requirements. Go ahead!")


@CheckRequire
def boards(req: HttpRequest):
    if req.method == "GET":
        params = req.GET
        boards = Board.objects.all().order_by('-created_time')
        return_data = {
            "boards": [
                # Only provide required fields to lower the latency of
                # transmitting LARGE packets through unstable network
                return_field(board.serialize(), ["id", "boardName", "createdAt", "userName"]) 
            for board in boards],
        }
        return request_success(return_data)
        
    
    elif req.method == "POST":
        body = json.loads(req.body.decode("utf-8"))
        
        board_state, board_name, user_name = check_for_board_data(body)
        
        # Find the corresponding user
        user = User.objects.filter(name=user_name).first()  # If not exists, return None
        
        if not user:
            # User not exists, create user
            user = User(name=user_name)
            user.save()
        
        # First we lookup if the board with the same name and the same user exists
        board = Board.objects.filter(board_name=board_name, user=user).first()
        
        if not board:
            # New an instance of Board type, then save it to the database
            board = Board(user=user, board_state=board_state, board_name=board_name)
            board.save()
            return request_success({"isCreate": True})
        
        else:
            # Board exists, change corresponding value of current `board`, then save it to the database
            board.board_state = board_state
            board.created_time = get_timestamp()
            board.save()
            return request_success({"isCreate": False})
    else:
        return BAD_METHOD


@CheckRequire
def boards_index(req: HttpRequest, index: any):
    
    idx = require({"index": index}, "index", "int", err_msg="Bad param [id]", err_code=-1)
    
    if req.method == "GET":
        params = req.GET
        board = Board.objects.filter(id=idx).first()  # Return None if not exists
        
        if board:
            return request_success(
                return_field(board.serialize(), ["board", "boardName", "userName"])
            )
        else:
            return request_failed(1, "Board not found", status_code=404)
    
    elif req.method == "DELETE":
        board = Board.objects.filter(id=idx).first()  # Return None if not exists, else corresponding instance
        
        if board:
            board.delete()
            return request_success()
            
        else:
            return request_failed(1, "Board not found", status_code=404)
    
    elif req.method == "PUT":
        body = json.loads(req.body.decode("utf-8"))
        
        # TODO Start: [Student] Finish PUT method for boards_index
        
        # 1. Check if body is valid and parse board_state, board_name and user_name from it
        #    Is there already a function for doing this?
        board_state, board_name, user_name = check_for_board_data(body)
        
        # 2. Using idx to filter board instance from Board.objects
        #    If it is None, return request_failed with code=1, message="Board not found" and status_code=404
        board = Board.objects.filter(id=idx).first()
        if not board:
            return request_failed(1, "Board not found", status_code=404)
        
        # 3. Find the corresponding user of the new board
        #    If the user does not exist, construct a new one and save it
        user = User.objects.filter(name=user_name).first()
        if not user:
            user = User(name=user_name)
            user.save()
        # 4. Find if the board with the same name and the same user exists and it is not the board to be updated
        #    If that board exists, return request_failed with code -2, message "Unique constraint failed" and http status code 400.
        existing_board = Board.objects.filter(board_name=board_name, user=user).exclude(id=idx).first()
        if existing_board:
            return request_failed(-2, "Unique constraint failed", status_code=400)
        
        # 5. Change corresponding properties of current `board`, and save it to the database
        #    Return request_success
        else:
            board.user = user
            board.board_state = board_state
            board.board_name = board_name
            board.created_time = get_timestamp()
            board.save()
        return request_success()
    
        # TODO End: [Student] Finish PUT method for boards_index
        
    else:
        return BAD_METHOD



# TODO Start: [Student] Finish view function for user_board
@CheckRequire
def user_board(req: HttpRequest, name:any):
    # 1. Check if name is valid and parse it to user_name
    # 该参数必须为非空且长度不大于 50 的字符串。
    # 若参数不符合要求均应当设置状态码为 400 Bad Request，错误响应格式为：
    username = require({"userName": name}, "userName", "string", err_msg="Bad param [userName]", err_code=-1)
    assert 0 < len(username) <= 50, "Bad param [userName]"
    
    user = User.objects.filter(name=username).first()
    if not user:
        return request_failed(1, "User not found", status_code=404)
    
    if req.method == "GET":
        params = req.GET
        boards = Board.objects.filter(user=user).order_by('-created_time')
        return_data = {
            "userName": username,
            "boards": [
                return_field(board.serialize(), ["id", "boardName", "createdAt", "userName"])
            for board in boards],
        }
        return request_success(return_data)

    elif req.method == "DELETE":
        # delete all boards of the user
        boards = Board.objects.filter(user=user)
        for board in boards:
            board.delete()
        return request_success()
    
    else:
        return  BAD_METHOD
        
# TODO End: [Student] Finish view function for user_board
