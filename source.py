# Tiny chess engine, make.fun tiny-chess-01. Original 0x88 code:
# negamax + alpha-beta, iterative deepening, TT, quiescence. Packed
# with `makefun compress`; deterministic (40k node budget, no clock).
# r33 = r25 (root score ordering) + history heuristic.
import os, json
from urllib.request import urlopen

ENV_URL = os.getenv("MAKEFUN_ENV_URL")


def post(path, payload):
    return json.load(urlopen(ENV_URL + path, json.dumps(payload).encode()))


VALUE = (0, 100, 320, 330, 500, 900, 0)
PST = [ord(c) * 5 - 375 for c in "KKKKUUUUMMOQLLMPKKKOLJIKLMMGKKKKACEECGKKEKMNELNOEKNOELMNCGKLACEEGIIIIKKKIKLMILLMIKMMIMMMILKKGIII" + "KKKKLMMM" + "JKKK" * 5 + "KKKL" + "GIIJIKKKIKLLJKLLKKLLILLLIKLKGIIJ" + "ECCA" * 4 + "GEECIGGGOOKKOQMK"]
KNIGHT_STEPS = (-33, -31, -18, -14, 14, 18, 31, 33)
DIAG_STEPS = (-17, -15, 15, 17)
ORTHO_STEPS = (-16, -1, 1, 16)
KING_STEPS = DIAG_STEPS + ORTHO_STEPS
FILE_MIRROR = (0, 1, 2, 3, 3, 2, 1, 0)
CASTLE_MASK = {4: 3, 116: 12, 0: 2, 7: 1, 112: 8, 119: 4}

TT = {}
KILLERS = [None] * 64
HIST = {}
INF = 100000
MATE = 1000000
NODE_CAP = 40000


class SearchAborted(Exception):
    pass


def square_name(sq):
    return chr(97 + (sq & 7)) + str((sq >> 4) + 1)


def move_uci(move):
    frm, to, promo = move
    return square_name(frm) + square_name(to) + ("", "x", "n", "b", "r", "q")[promo]


def parse_fen(fen):
    global board, side, castling, wk_sq, bk_sq, stack, ep_sq
    words = fen.split()
    board = [0] * 128
    stack = []
    sq = 112
    for ch in words[0]:
        if ch == "/":
            sq -= 24
        elif "/" < ch < ":":
            sq += int(ch)
        else:
            board[sq] = " PNBRQK".index(ch.upper()) * ((ch < "a") * 2 - 1)
            sq += 1
    side = 1 - 2 * (words[1] == "b")
    castling = sum((c in words[2]) << i for i, c in enumerate("KQkq"))
    ep_sq = None
    if len(words) > 3 and words[3] != "-":
        ep_sq = (int(words[3][1]) - 1) * 16 + ord(words[3][0]) - 97
    wk_sq = board.index(6)
    bk_sq = board.index(-6)


def attacked(sq, by):
    b = board
    for steps, piece in (((-15 * by, -17 * by), 1), (KNIGHT_STEPS, 2), (KING_STEPS, 6)):
        for d in steps:
            t = sq + d
            if not (t & 0x88) and b[t] == by * piece:
                return 1
    for steps, piece, queen in ((DIAG_STEPS, 3, 5), (ORTHO_STEPS, 4, 5)):
        for d in steps:
            t = sq + d
            while not (t & 0x88):
                if b[t]:
                    if b[t] in (by * piece, by * queen):
                        return 1
                    break
                t += d
    return 0


def gen_moves(captures_only):
    moves = []
    add = moves.append
    b = board
    w = side

    def push(frm, to):
        if (to >> 4) == 7 * (side > 0):
            for promo in (5, 4, 3, 2):
                add((frm, to, promo))
        else:
            add((frm, to, 0))

    for sq, piece in enumerate(b):
        if piece * w <= 0:
            continue
        kind = abs(piece)
        if kind == 1:
            step = 16 * w
            to = sq + step
            if not b[to]:
                if (to >> 4) == 7 * (w > 0):
                    push(sq, to)
                elif not captures_only:
                    add((sq, to, 0))
                    if (sq >> 4) == 1 + 5 * (w < 0) and not b[sq + 2 * step]:
                        add((sq, sq + 2 * step, 0))
            for to in (sq + step - 1, sq + step + 1):
                if not (to & 0x88) and (b[to] * w < 0 or to == ep_sq):
                    push(sq, to)
        else:
            for d in (KNIGHT_STEPS, DIAG_STEPS, ORTHO_STEPS, KING_STEPS, KING_STEPS)[kind - 2]:
                to = sq + d
                while not (to & 0x88):
                    if b[to]:
                        if b[to] * w < 0:
                            add((sq, to, 0))
                        break
                    if not captures_only:
                        add((sq, to, 0))
                    if kind % 4 == 2:
                        break
                    to += d
    if not captures_only:
        king_sq = 4 + 112 * (w < 0)
        for mask, sgn in ((1, 1), (2, -1)):
            if (castling & mask << 2 * (w < 0)
                    and not (attacked(king_sq, -w) or attacked(king_sq + sgn, -w))
                    and not (b[king_sq + sgn] or b[king_sq + 2 * sgn])
                    and (sgn > 0 or not b[king_sq + 3 * sgn])):
                add((king_sq, king_sq + 2 * sgn, 0))
    return moves


def make_move(move):
    global side, castling, wk_sq, bk_sq, ep_sq
    frm, to, promo = move
    b = board
    captured = b[to]
    captured_sq = to
    if abs(b[frm]) == 1 and to == ep_sq and not captured:
        captured_sq = to - 16 * side
        captured = b[captured_sq]
    stack.append((move, captured, castling, ep_sq))
    b[to] = promo * side or b[frm]
    b[frm] = 0
    if captured_sq != to:
        b[captured_sq] = 0
    if abs(b[to]) > 5:
        if side > 0:
            wk_sq = to
        else:
            bk_sq = to
        if abs(to - frm) == 2:
            rook_from = 112 * (side < 0) + 7 * (to > frm)
            b[(to + frm) // 2] = b[rook_from]
            b[rook_from] = 0
    if abs(b[to]) == 1 and abs(to - frm) == 32:
        ep_sq = (frm + to) // 2
    else:
        ep_sq = None
    castling &= ~CASTLE_MASK.get(frm, 0) & ~CASTLE_MASK.get(to, 0)
    side = -side


def unmake_move():
    global side, castling, wk_sq, bk_sq, ep_sq
    move, captured, castling, ep_sq = stack.pop()
    frm, to, promo = move
    side = -side
    b = board
    b[frm] = side if promo else b[to]
    b[to] = 0
    if captured:
        if to == ep_sq and abs(b[frm]) == 1:
            b[to - 16 * side] = captured
        else:
            b[to] = captured
    if abs(b[frm]) > 5:
        if side > 0:
            wk_sq = frm
        else:
            bk_sq = frm
        if abs(to - frm) == 2:
            rook_from = 112 * (side < 0) + 7 * (to > frm)
            b[rook_from] = b[(to + frm) // 2]
            b[(to + frm) // 2] = 0


def legal_moves(moves):
    out = []
    king = (bk_sq, wk_sq)[side > 0]
    in_check = attacked(king, -side)
    for move in moves:
        delta = move[0] - king
        if (in_check or board[move[0]] == 6 * side or move[1] == ep_sq
                or not (delta % 15 and delta % 17 and delta % 16 and abs(delta) > 7)):
            make_move(move)
            if not attacked((wk_sq, bk_sq)[side > 0], side):
                out.append(move)
            unmake_move()
        else:
            out.append(move)
    return out


def evaluate():
    score = 0
    for sq, piece in enumerate(board):
        if piece:
            kind = abs(piece)
            rank = sq >> 4
            file = sq & 7
            value = VALUE[kind] + PST[(kind - 1) * 32 + (rank ^ 7 * (piece > 0)) * 4 + FILE_MIRROR[file]]
            score += value * (piece > 0) * 2 - value
            if kind == 1:
                step = 16 if piece > 0 else -16
                adv = (rank - 1) if piece > 0 else (6 - rank)
                t = sq + step
                passed = True
                while not t & 0x88:
                    if board[t] == -piece or (t & 7 and board[t - 1] == -piece) or ((t & 7) < 7 and board[t + 1] == -piece):
                        passed = False
                        break
                    t += step
                if passed:
                    score += adv * adv * 2 * (2 * (piece > 0) - 1)
    return score * side


def search(depth, alpha, beta, ply, qs_ply):
    global nodes
    nodes += 1
    if nodes > NODE_CAP:
        raise SearchAborted
    if depth <= 0:
        if qs_ply >= 6:
            return evaluate()
        in_check = attacked((wk_sq, bk_sq)[side < 0], -side)
        moves = legal_moves(gen_moves(not in_check))
        if in_check and not moves:
            return -INF + ply
        score = evaluate() if not in_check else -MATE
        if score >= beta:
            return beta
        if score > alpha:
            alpha = score
        for move in moves:
            make_move(move)
            score = -search(0, -beta, -alpha, ply + 1, qs_ply + 1)
            unmake_move()
            if score >= beta:
                return beta
            if score > alpha:
                alpha = score
        return alpha
    key = (tuple(board), side, castling, ep_sq)
    entry = TT.get(key)
    tt_move = entry and entry[3]
    if (entry and entry[0] >= depth
            and (entry[1] != 1 or entry[2] <= alpha)
            and (entry[1] != 2 or entry[2] >= beta)):
        return entry[2]
    moves = legal_moves(gen_moves(0))
    if not moves:
        return -INF + ply if attacked((wk_sq, bk_sq)[side < 0], -side) else 0
    moves.sort(key=lambda m: -(MATE * (m == tt_move) + 4000 * (m == KILLERS[ply]) + min(HIST.get(m, 0), 2000) + VALUE[abs(board[m[1]])] + 20 * VALUE[m[2]]))
    alpha_orig = alpha
    best = best_move = -MATE
    for move in moves:
        make_move(move)
        score = -search(depth - 1, -beta, -alpha, ply + 1, 0)
        unmake_move()
        if score > best:
            best, best_move = score, move
        if score > alpha:
            alpha = score
        if alpha >= beta:
            KILLERS[ply] = move
            if not board[move[1]] and move[1] != ep_sq and not move[2]:
                HIST[move] = HIST.get(move, 0) + depth * depth
            break
    TT[key] = (depth, (best >= beta) * 2 + (best <= alpha_orig), best, best_move)
    return best


def think():
    global nodes
    nodes = 0
    TT.clear()
    HIST.clear()
    moves = legal_moves(gen_moves(0))
    if not moves:
        return None
    best = moves[0]
    sc = {}
    try:
        for depth in range(1, 64):
            moves.sort(key=lambda m: -sc.get(m, 0))
            alpha = -MATE
            candidate = best
            ns = {}
            for move in moves:
                make_move(move)
                score = -search(depth - 1, -MATE, -alpha, 1, 0)
                unmake_move()
                ns[move] = score
                if score > alpha:
                    alpha = score
                    candidate = move
            sc = ns
            best = candidate
    except SearchAborted:
        pass
    return best


def main():
    while True:
        game = post("/game", {})
        if game["status"][0] == "d":
            break
        while game["status"][0] == "y":
            parse_fen(game["fen"])
            move = think()
            game = post("/move", {"game": game["game"],
                                  "move": move_uci(move) if move else game["legal_moves"][0]})


if __name__ == "__main__":
    main()
