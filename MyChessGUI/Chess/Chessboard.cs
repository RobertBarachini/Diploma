using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Drawing;
using System.IO;
using System.Linq;
using System.Security.Cryptography;
using System.Text;
using System.Threading;
using System.Threading.Tasks;
using System.Windows.Forms;

namespace Chess
{
    // TODO
    // - normal legal moves
    // - enpasan
    // - castling
    // - pins
    // - promotions
    // - check
    // - mate

    public class Chessboard : Control
    {
        public Color colorLight = Color.FromArgb(255, 253, 244);
        public Color colorDark = Color.FromArgb(0, 150, 30);
        public Color colorPiecesLight = Color.White;
        public Color colorPiecesDark = Color.Black;

        public LinkedList<ChessPiece> piecesLight;
        //public LinkedList<ChessPiece> takenLight;
        public LinkedList<ChessPiece> piecesDark;
        //public LinkedList<ChessPiece> takenDark;

        // Top left is 0,0 - playing as white is mirrored across the diagonal - 7,7
        public ChessPiece[,] playingField;

        private Point mouse;
        private Point mouseDownP;
        private LinkedList<Point> piecePickedValidMoves;
        private bool mouseDown;
        private ChessPiece piecePicked;
        private ChessPiece kingLight;
        private ChessPiece kingDark;
        private Point oldSquareLight;
        private Point oldSquareDark;
        private Random r1;

        private bool lightTurn;
        public bool facingLight; // "Playing as white"

        MoveGeneratorInterface moveGeneratorInterface;

        public Chessboard()
        {
            SetUpBoard();

            DoubleBuffered = true;
            BackColor = Color.FromArgb(58, 58, 58);
            r1 = new Random();
            r1.Next(0, 100);

            MouseMove += Chessboard_MouseMove;
            MouseDown += Chessboard_MouseDown;
            MouseUp += Chessboard_MouseUp;

            moveGeneratorInterface = new MoveGeneratorInterface();
        }

        public bool IsLightTurn()
        {
            return lightTurn;
        }

        private void Chessboard_MouseDown(object sender, MouseEventArgs e)
        {
            if (mouseDown == false)
            {
                mouseDownP = e.Location;
                mouseDown = true;
                Point square = GetSquareFromPoint(mouseDownP);
                if (facingLight)
                {
                    square.X = square.X * -1 + 7;
                    square.Y = square.Y * -1 + 7;
                }

                piecePicked = playingField[square.X, square.Y];
                if (piecePicked != null)
                {
                    piecePickedValidMoves = GetValidMoves(piecePicked);
                }

                if (piecePicked != null && ((piecePicked.pieceColor == ChessPiece.PieceColor.Light && lightTurn) || (piecePicked.pieceColor == ChessPiece.PieceColor.Dark && !lightTurn)))
                {
                    if (piecePicked.pieceColor == ChessPiece.PieceColor.Light)
                    {
                        oldSquareLight = square;
                        //piecesLight.Remove(piecePicked);
                    }
                    else if (piecePicked.pieceColor == ChessPiece.PieceColor.Dark)
                    {
                        oldSquareDark = square;
                        //piecesDark.Remove(piecePicked);
                    }

                    playingField[piecePicked.Xindex, piecePicked.Yindex] = null;
                }
                else
                {
                    piecePicked = null;
                    mouseDown = false;
                }
            }
        }

        private void Chessboard_MouseUp(object sender, MouseEventArgs e)
        {
            if (mouseDown)
            {
                mouseDown = false;

                Point square = GetSquareFromPoint(e.Location);
                if (facingLight)
                {
                    square.X = square.X * -1 + 7;
                    square.Y = square.Y * -1 + 7;
                }

                if (piecePicked != null)
                {
                    bool movedToLegal = false;
                    foreach (Point p in piecePickedValidMoves)
                    {
                        if (square.X == p.X && square.Y == p.Y)
                        {
                            movedToLegal = true;
                            break;
                        }
                    }

                    if (movedToLegal == false)
                    {
                        if (piecePicked.pieceColor == ChessPiece.PieceColor.Light)
                        {
                            square = oldSquareLight;
                        }
                        else if (piecePicked.pieceColor == ChessPiece.PieceColor.Dark)
                        {
                            square = oldSquareDark;
                        }
                    }

                    int brk1 = 0;
                    MovePiece(piecePicked, square.X, square.Y);
                    int brk2 = 0;

                    //if (piecePicked.pieceColor == ChessPiece.PieceColor.Light)
                    //{
                    //    piecesLight.AddLast(piecePicked);
                    //}
                    //else if (piecePicked.pieceColor == ChessPiece.PieceColor.Dark)
                    //{
                    //    piecesDark.AddLast(piecePicked);
                    //}
                    if (piecePicked != null)
                    {
                        //playingField[piecePicked.Xindex, piecePicked.Yindex] = piecePicked;
                    }

                    piecePickedValidMoves = new LinkedList<Point>();
                    int brk3 = 0;
                }
            }

            piecePicked = null;
        }

        private void Chessboard_MouseMove(object sender, MouseEventArgs e)
        {
            mouse = e.Location;
            Invalidate();
        }

        private Point GetSquareFromPoint(Point point)
        {
            int squareX = Math.Max(Math.Min(point.X / (Width / 8), 7), 0);
            int squareY = Math.Max(Math.Min(point.Y / (Height / 8), 7), 0);

            return new Point(squareX, squareY);
        }

        private string GetPieceFilename(ChessPiece c)
        {
            string filename = "";
            if (c.pieceColor == ChessPiece.PieceColor.Light)
            {
                if (c.pieceType == ChessPiece.PieceType.Pawn)
                {
                    filename = "Light_Pawn.png";
                }
                else if (c.pieceType == ChessPiece.PieceType.Rook)
                {
                    filename = "Light_Rook.png";
                }
                else if (c.pieceType == ChessPiece.PieceType.Knight)
                {
                    filename = "Light_Knight.png";
                }
                else if (c.pieceType == ChessPiece.PieceType.Bishop)
                {
                    filename = "Light_Bishop.png";
                }
                else if (c.pieceType == ChessPiece.PieceType.Queen)
                {
                    filename = "Light_Queen.png";
                }
                else if (c.pieceType == ChessPiece.PieceType.King)
                {
                    filename = "Light_King.png";
                }
            }
            else
            {
                if (c.pieceType == ChessPiece.PieceType.Pawn)
                {
                    filename = "Dark_Pawn.png";
                }
                else if (c.pieceType == ChessPiece.PieceType.Rook)
                {
                    filename = "Dark_Rook.png";
                }
                else if (c.pieceType == ChessPiece.PieceType.Knight)
                {
                    filename = "Dark_Knight.png";
                }
                else if (c.pieceType == ChessPiece.PieceType.Bishop)
                {
                    filename = "Dark_Bishop.png";
                }
                else if (c.pieceType == ChessPiece.PieceType.Queen)
                {
                    filename = "Dark_Queen.png";
                }
                else if (c.pieceType == ChessPiece.PieceType.King)
                {
                    filename = "Dark_King.png";
                }
            }

            return filename;
        }

        public string ChessPiecePositionToString(int indexX, int indexY)
        {
            string output = "";

            indexX = indexX * -1 + 7;
            if (indexX == 0) { output = "A"; }
            else if (indexX == 1) { output = "B"; }
            else if (indexX == 2) { output = "C"; }
            else if (indexX == 3) { output = "D"; }
            else if (indexX == 4) { output = "E"; }
            else if (indexX == 5) { output = "F"; }
            else if (indexX == 6) { output = "G"; }
            else if (indexX == 7) { output = "H"; }
            else { output = "X"; }

            if (indexY < 0 || indexY > 7)
            {
                return output + " X";
            }

            return output + " " + (indexY + 1).ToString();
        }

        protected override void OnPaint(PaintEventArgs e)
        {
            base.OnPaint(e);
            e.Graphics.SmoothingMode = System.Drawing.Drawing2D.SmoothingMode.AntiAlias;

            //g.InterpolationMode = System.Drawing.Drawing2D.InterpolationMode.HighQualityBilinear;

            int w = Width;
            int h = Height;

            SolidBrush sb1 = new SolidBrush(colorLight);

            Point square = GetSquareFromPoint(mouse);
            Point squarePlaying = GetSquareFromPoint(mouse);
            if (facingLight)
            {
                squarePlaying.X = squarePlaying.X * -1 + 7;
                squarePlaying.Y = squarePlaying.Y * -1 + 7;
            }
            ChessPiece chosenOne = playingField[squarePlaying.X, squarePlaying.Y];

            // Board
            for (int i = 0; i < 8; i++)
            {
                for (int j = 0; j < 8; j++)
                {
                    e.Graphics.FillRectangle(sb1, j * (w / 8), i * (h / 8), w / 8, h / 8);
                    sb1.Color = sb1.Color == colorLight ? colorDark : colorLight;
                }
                sb1.Color = sb1.Color == colorLight ? colorDark : colorLight;
            }

            // Highlights
            sb1.Color = Color.FromArgb(150, Color.Red);
            foreach (Point p in piecePickedValidMoves)
            {
                Point pN = new Point(p.X, p.Y);
                if (facingLight)
                {
                    pN.X = pN.X * -1 + 7;
                    pN.Y = pN.Y * -1 + 7;
                }
                e.Graphics.FillRectangle(sb1, pN.X * (w / 8), pN.Y * (h / 8), w / 8, h / 8);
            }

            //e.Graphics.DrawLine(new Pen(Color.Red, 3), 0, 0, mouse.X, mouse.Y);

            sb1.Color = Color.FromArgb(150, Color.Yellow);
            e.Graphics.FillRectangle(sb1, square.X * (w / 8), square.Y * (h / 8), w / 8, h / 8);

            //if (piecePicked != null)
            //{
            //    LinkedList<Point> allValid = GetAllValidMoves(piecePicked.pieceColor == ChessPiece.PieceColor.Light ? ChessPiece.PieceColor.Light : ChessPiece.PieceColor.Dark);
            //    sb1.Color = Color.FromArgb(150, Color.LightBlue);
            //    foreach (Point p in allValid)
            //    {
            //        Point pN = new Point(p.X, p.Y);
            //        if (facingLight)
            //        {
            //            pN.X = pN.X * -1 + 7;
            //            pN.Y = pN.Y * -1 + 7;
            //        }
            //        e.Graphics.FillRectangle(sb1, pN.X * (w / 8), pN.Y * (h / 8), w / 8, h / 8);
            //    }
            //}

            // Light pieces
            string piecesDirectory = "pieces";
            foreach (ChessPiece c in piecesLight)
            {
                if (c != piecePicked)
                {
                    Image i = Image.FromFile(Path.Combine(piecesDirectory, GetPieceFilename(c)));
                    if (facingLight)
                    {
                        e.Graphics.DrawImage(i, new Rectangle((c.Xindex * -1 + 7) * (w / 8), (c.Yindex * -1 + 7) * (h / 8), (int)((w / 8) * 1), (int)((h / 8) * 1)));
                    }
                    else
                    {
                        e.Graphics.DrawImage(i, new Rectangle(c.Xindex * (w / 8), c.Yindex * (h / 8), (int)((w / 8) * 1), (int)((h / 8) * 1)));
                    }

                    i.Dispose();
                }
            }

            // Dark pieces
            foreach (ChessPiece c in piecesDark)
            {
                if (c != piecePicked)
                {
                    Image i = Image.FromFile(Path.Combine(piecesDirectory, GetPieceFilename(c)));
                    if (facingLight)
                    {
                        e.Graphics.DrawImage(i, new Rectangle((c.Xindex * -1 + 7) * (w / 8), (c.Yindex * -1 + 7) * (h / 8), (int)((w / 8) * 1), (int)((h / 8) * 1)));
                    }
                    else
                    {
                        e.Graphics.DrawImage(i, new Rectangle(c.Xindex * (w / 8), c.Yindex * (h / 8), (int)((w / 8) * 1), (int)((h / 8) * 1)));
                    }
                    i.Dispose();
                }
            }

            // Piece drag
            if (mouseDown)
            {
                Image i = Image.FromFile(Path.Combine(piecesDirectory, GetPieceFilename(piecePicked)));
                e.Graphics.DrawImage(i, new Rectangle(mouse.X - (w / 16), mouse.Y - (h / 16), (int)((w / 8) * 1), (int)((h / 8) * 1)));
                i.Dispose();
            }

            // Text
            sb1.Color = Color.FromArgb(255, Color.OrangeRed);
            string chosenOneString = "";
            if (chosenOne == null)
            {
                chosenOneString = ChessPiecePositionToString(squarePlaying.X, squarePlaying.Y).Replace(" ", "");
            }
            else
            {
                chosenOneString = chosenOne.pieceColor.ToString() + " " + chosenOne.pieceType.ToString() + " " + ChessPiecePositionToString(chosenOne.Xindex, chosenOne.Yindex).Replace(" ", "");
            }
            e.Graphics.DrawString(chosenOneString, new Font(new FontFamily("Segoe UI"), 40, GraphicsUnit.Pixel), sb1, 0, (h / 8) * 2);

            sb1.Dispose();
        }

        private bool KingAttacked(ChessPiece.PieceColor enemyColor)
        {
            string pos1 = BoardToString();
            if (enemyColor == ChessPiece.PieceColor.Light)
            {
                if (SquareAttacked(new Point(kingDark.Xindex, kingDark.Yindex), ChessPiece.PieceColor.Dark))
                {
                    return true;
                }
            }
            else if (enemyColor == ChessPiece.PieceColor.Dark)
            {
                if (SquareAttacked(new Point(kingLight.Xindex, kingLight.Yindex), ChessPiece.PieceColor.Light))
                {
                    return true;
                }
            }
            return false;
        }

        private bool SquareAttacked(Point square, ChessPiece.PieceColor pieceColor)
        {
            if (pieceColor == ChessPiece.PieceColor.Light)
            {
                foreach (ChessPiece c in piecesDark)
                {
                    if (SquareAttacked(c, square))
                    {
                        return true;
                    }
                }
            }
            else if (pieceColor == ChessPiece.PieceColor.Dark)
            {
                foreach (ChessPiece c in piecesLight)
                {
                    if (SquareAttacked(c, square))
                    {
                        return true;
                    }
                }
            }

            return false;
        }

        private bool SquareAttacked(ChessPiece piece, Point square)
        {
            LinkedList<Point> squares = new LinkedList<Point>();

            if (piece.pieceType == ChessPiece.PieceType.Pawn)
            {
                if (piece.pieceColor == ChessPiece.PieceColor.Light)
                {
                    // Take left
                    if (piece.Xindex - 1 == square.X && piece.Yindex + 1 == square.Y)
                    {
                        return true;
                    }

                    // Take right
                    if (piece.Xindex + 1 == square.X && piece.Yindex + 1 == square.Y)
                    {
                        return true;
                    }
                }
                else if (piece.pieceColor == ChessPiece.PieceColor.Dark)
                {
                    // Take left
                    if (piece.Xindex - 1 == square.X && piece.Yindex - 1 == square.Y)
                    {
                        return true;
                    }

                    // Take right
                    if (piece.Xindex + 1 == square.X && piece.Yindex - 1 == square.Y)
                    {
                        return true;
                    }
                }
            }
            else if (piece.pieceType == ChessPiece.PieceType.Knight)
            {
                if (piece.Xindex - 2 == square.X && piece.Yindex + 1 == square.Y)
                {
                    return true;
                }
                if (piece.Xindex - 1 == square.X && piece.Yindex + 2 == square.Y)
                {
                    return true;
                }

                if (piece.Xindex + 2 == square.X && piece.Yindex - 1 == square.Y)
                {
                    return true;
                }
                if (piece.Xindex + 1 == square.X && piece.Yindex - 2 == square.Y)
                {
                    return true;
                }

                if (piece.Xindex - 2 == square.X && piece.Yindex - 1 == square.Y)
                {
                    return true;
                }
                if (piece.Xindex - 1 == square.X && piece.Yindex - 2 == square.Y)
                {
                    return true;
                }

                if (piece.Xindex + 2 == square.X && piece.Yindex + 1 == square.Y)
                {
                    return true;
                }
                if (piece.Xindex + 1 == square.X && piece.Yindex + 2 == square.Y)
                {
                    return true;
                }
            }
            else if (piece.pieceType == ChessPiece.PieceType.Rook)
            {
                // Up
                for (int i = piece.Yindex + 1; i < 8; i++)
                {
                    if (playingField[piece.Xindex, i] == null || (playingField[piece.Xindex, i] != null))
                    {
                        if (piece.Xindex == square.X && i == square.Y)
                        {
                            return true;
                        }

                        if (playingField[piece.Xindex, i] != null)
                        {
                            break;
                        }
                    }
                    else
                    {
                        break;
                    }
                }

                // Down
                for (int i = piece.Yindex - 1; i > -1; i--)
                {
                    if (playingField[piece.Xindex, i] == null || (playingField[piece.Xindex, i] != null))
                    {
                        if (piece.Xindex == square.X && i == square.Y)
                        {
                            return true;
                        }

                        if (playingField[piece.Xindex, i] != null)
                        {
                            break;
                        }
                    }
                    else
                    {
                        break;
                    }
                }

                // Left
                for (int i = piece.Xindex - 1; i > -1; i--)
                {
                    if (playingField[i, piece.Yindex] == null || (playingField[i, piece.Yindex] != null))
                    {
                        if (i == square.X && piece.Yindex == square.Y)
                        {
                            return true;
                        }

                        if (playingField[i, piece.Yindex] != null)
                        {
                            break;
                        }
                    }
                    else
                    {
                        break;
                    }
                }

                // Right
                for (int i = piece.Xindex + 1; i < 8; i++)
                {
                    if (playingField[i, piece.Yindex] == null || (playingField[i, piece.Yindex] != null))
                    {
                        if (i == square.X && piece.Yindex == square.Y)
                        {
                            return true;
                        }

                        if (playingField[i, piece.Yindex] != null)
                        {
                            break;
                        }
                    }
                    else
                    {
                        break;
                    }
                }
            }
            else if (piece.pieceType == ChessPiece.PieceType.Bishop)
            {
                // Up left
                for (int i = 1; piece.Xindex - i > -1 && piece.Yindex + i < 8; i++)
                {
                    if (playingField[piece.Xindex - i, piece.Yindex + i] == null || (playingField[piece.Xindex - i, piece.Yindex + i] != null))
                    {
                        if (piece.Xindex - i == square.X && piece.Yindex + i == square.Y)
                        {
                            return true;
                        }

                        if (playingField[piece.Xindex - i, piece.Yindex + i] != null)
                        {
                            break;
                        }
                    }
                    else
                    {
                        break;
                    }
                }

                // Up right
                for (int i = 1; piece.Xindex + i < 8 && piece.Yindex + i < 8; i++)
                {
                    if (playingField[piece.Xindex + i, piece.Yindex + i] == null || (playingField[piece.Xindex + i, piece.Yindex + i] != null))
                    {
                        if (piece.Xindex + i == square.X && piece.Yindex + i == square.Y)
                        {
                            return true;
                        }

                        if (playingField[piece.Xindex + i, piece.Yindex + i] != null)
                        {
                            break;
                        }
                    }
                    else
                    {
                        break;
                    }
                }

                // Down left
                for (int i = 1; piece.Xindex - i > -1 && piece.Yindex - i > -1; i++)
                {
                    if (playingField[piece.Xindex - i, piece.Yindex - i] == null || (playingField[piece.Xindex - i, piece.Yindex - i] != null))
                    {
                        if (piece.Xindex - i == square.X && piece.Yindex - i == square.Y)
                        {
                            return true;
                        }

                        if (playingField[piece.Xindex - i, piece.Yindex - i] != null)
                        {
                            break;
                        }
                    }
                    else
                    {
                        break;
                    }
                }

                // Down right
                for (int i = 1; piece.Xindex + i < 8 && piece.Yindex - i > -1; i++)
                {
                    if (playingField[piece.Xindex + i, piece.Yindex - i] == null || (playingField[piece.Xindex + i, piece.Yindex - i] != null))
                    {
                        if (piece.Xindex + i == square.X && piece.Yindex - i == square.Y)
                        {
                            return true;
                        }

                        if (playingField[piece.Xindex + i, piece.Yindex - i] != null)
                        {
                            break;
                        }
                    }
                    else
                    {
                        break;
                    }
                }
            }
            else if (piece.pieceType == ChessPiece.PieceType.Queen)
            {
                // Queen = Bishop + Rook

                // Up
                for (int i = piece.Yindex + 1; i < 8; i++)
                {
                    if (playingField[piece.Xindex, i] == null || (playingField[piece.Xindex, i] != null))
                    {
                        if (piece.Xindex == square.X && i == square.Y)
                        {
                            return true;
                        }

                        if (playingField[piece.Xindex, i] != null)
                        {
                            break;
                        }
                    }
                    else
                    {
                        break;
                    }
                }

                // Down
                for (int i = piece.Yindex - 1; i > -1; i--)
                {
                    if (playingField[piece.Xindex, i] == null || (playingField[piece.Xindex, i] != null))
                    {
                        if (piece.Xindex == square.X && i == square.Y)
                        {
                            return true;
                        }

                        if (playingField[piece.Xindex, i] != null)
                        {
                            break;
                        }
                    }
                    else
                    {
                        break;
                    }
                }

                // Left
                for (int i = piece.Xindex - 1; i > -1; i--)
                {
                    if (playingField[i, piece.Yindex] == null || (playingField[i, piece.Yindex] != null))
                    {
                        if (i == square.X && piece.Yindex == square.Y)
                        {
                            return true;
                        }

                        if (playingField[i, piece.Yindex] != null)
                        {
                            break;
                        }
                    }
                    else
                    {
                        break;
                    }
                }

                // Right
                for (int i = piece.Xindex + 1; i < 8; i++)
                {
                    if (playingField[i, piece.Yindex] == null || (playingField[i, piece.Yindex] != null))
                    {
                        if (i == square.X && piece.Yindex == square.Y)
                        {
                            return true;
                        }

                        if (playingField[i, piece.Yindex] != null)
                        {
                            break;
                        }
                    }
                    else
                    {
                        break;
                    }
                }

                // Up left
                for (int i = 1; piece.Xindex - i > -1 && piece.Yindex + i < 8; i++)
                {
                    if (playingField[piece.Xindex - i, piece.Yindex + i] == null || (playingField[piece.Xindex - i, piece.Yindex + i] != null))
                    {
                        if (piece.Xindex - i == square.X && piece.Yindex + i == square.Y)
                        {
                            return true;
                        }

                        if (playingField[piece.Xindex - i, piece.Yindex + i] != null)
                        {
                            break;
                        }
                    }
                    else
                    {
                        break;
                    }
                }

                // Up right
                for (int i = 1; piece.Xindex + i < 8 && piece.Yindex + i < 8; i++)
                {
                    if (playingField[piece.Xindex + i, piece.Yindex + i] == null || (playingField[piece.Xindex + i, piece.Yindex + i] != null))
                    {
                        if (piece.Xindex + i == square.X && piece.Yindex + i == square.Y)
                        {
                            return true;
                        }

                        if (playingField[piece.Xindex + i, piece.Yindex + i] != null)
                        {
                            break;
                        }
                    }
                    else
                    {
                        break;
                    }
                }

                // Down left
                for (int i = 1; piece.Xindex - i > -1 && piece.Yindex - i > -1; i++)
                {
                    if (playingField[piece.Xindex - i, piece.Yindex - i] == null || (playingField[piece.Xindex - i, piece.Yindex - i] != null))
                    {
                        if (piece.Xindex - i == square.X && piece.Yindex - i == square.Y)
                        {
                            return true;
                        }

                        if (playingField[piece.Xindex - i, piece.Yindex - i] != null)
                        {
                            break;
                        }
                    }
                    else
                    {
                        break;
                    }
                }

                // Down right
                for (int i = 1; piece.Xindex + i < 8 && piece.Yindex - i > -1; i++)
                {
                    if (playingField[piece.Xindex + i, piece.Yindex - i] == null || (playingField[piece.Xindex + i, piece.Yindex - i] != null))
                    {
                        if (piece.Xindex + i == square.X && piece.Yindex - i == square.Y)
                        {
                            return true;
                        }

                        if (playingField[piece.Xindex + i, piece.Yindex - i] != null)
                        {
                            break;
                        }
                    }
                    else
                    {
                        break;
                    }
                }
            }
            else if (piece.pieceType == ChessPiece.PieceType.King)
            {
                // 1 move queen

                // Up
                for (int i = piece.Yindex + 1; i < 8; i++)
                {
                    if (playingField[piece.Xindex, i] == null || (playingField[piece.Xindex, i] != null))
                    {
                        if (piece.Xindex == square.X && i == square.Y)
                        {
                            return true;
                        }
                    }
                    break;
                }

                // Down
                for (int i = piece.Yindex - 1; i > -1; i--)
                {
                    if (playingField[piece.Xindex, i] == null || (playingField[piece.Xindex, i] != null))
                    {
                        if (piece.Xindex == square.X && i == square.Y)
                        {
                            return true;
                        }
                    }
                    break;
                }

                // Left
                for (int i = piece.Xindex - 1; i > -1; i--)
                {
                    if (playingField[i, piece.Yindex] == null || (playingField[i, piece.Yindex] != null))
                    {
                        if (i == square.X && piece.Yindex == square.Y)
                        {
                            return true;
                        }
                    }
                    break;
                }

                // Right
                for (int i = piece.Xindex + 1; i < 8; i++)
                {
                    if (playingField[i, piece.Yindex] == null || (playingField[i, piece.Yindex] != null))
                    {
                        if (i == square.X && piece.Yindex == square.Y)
                        {
                            return true;
                        }
                    }
                    break;
                }

                // Up left
                for (int i = 1; piece.Xindex - i > -1 && piece.Yindex + i < 8; i++)
                {
                    if (playingField[piece.Xindex - i, piece.Yindex + i] == null || (playingField[piece.Xindex - i, piece.Yindex + i] != null))
                    {
                        if (piece.Xindex - i == square.X && piece.Yindex + i == square.Y)
                        {
                            return true;
                        }
                    }
                    break;
                }

                // Up right
                for (int i = 1; piece.Xindex + i < 8 && piece.Yindex + i < 8; i++)
                {
                    if (playingField[piece.Xindex + i, piece.Yindex + i] == null || (playingField[piece.Xindex + i, piece.Yindex + i] != null))
                    {
                        if (piece.Xindex + i == square.X && piece.Yindex + i == square.Y)
                        {
                            return true;
                        }
                    }
                    break;
                }

                // Down left
                for (int i = 1; piece.Xindex - i > -1 && piece.Yindex - i > -1; i++)
                {
                    if (playingField[piece.Xindex - i, piece.Yindex - i] == null || (playingField[piece.Xindex - i, piece.Yindex - i] != null))
                    {
                        if (piece.Xindex - i == square.X && piece.Yindex - i == square.Y)
                        {
                            return true;
                        }
                    }
                    break;
                }

                // Down right
                for (int i = 1; piece.Xindex + i < 8 && piece.Yindex - i > -1; i++)
                {
                    if (playingField[piece.Xindex + i, piece.Yindex - i] == null || (playingField[piece.Xindex + i, piece.Yindex - i] != null))
                    {
                        if (piece.Xindex + i == square.X && piece.Yindex - i == square.Y)
                        {
                            return true;
                        }
                    }
                    break;
                }
            }

            return false;
        }

        private bool SimulatedMoveOK(ChessPiece piece, Point newLocation)
        {
            string pos1 = BoardToString();
            // Simulate new position
            Point pieceOldPosition = new Point(piece.Xindex, piece.Yindex);
            ChessPiece pieceOnNewSquare = playingField[newLocation.X, newLocation.Y];
            if (pieceOnNewSquare != null)
            {
                if (pieceOnNewSquare.pieceColor == ChessPiece.PieceColor.Light)
                {
                    piecesLight.Remove(pieceOnNewSquare);
                }
                else
                {
                    piecesDark.Remove(pieceOnNewSquare);
                }
            }
            playingField[piece.Xindex, piece.Yindex] = null;
            playingField[newLocation.X, newLocation.Y] = piece;
            piece.Xindex = newLocation.X;
            piece.Yindex = newLocation.Y;

            // Check if king is attacked in new position
            bool kingAttackedInNewPosition = false;
            if (KingAttacked(piece.pieceColor == ChessPiece.PieceColor.Light ? ChessPiece.PieceColor.Dark : ChessPiece.PieceColor.Light))
            {
                kingAttackedInNewPosition = true;
            }

            // Renew old position
            piece.Xindex = pieceOldPosition.X;
            piece.Yindex = pieceOldPosition.Y;
            playingField[pieceOldPosition.X, pieceOldPosition.Y] = piece;
            playingField[newLocation.X, newLocation.Y] = pieceOnNewSquare;

            if (pieceOnNewSquare != null)
            {
                if (pieceOnNewSquare.pieceColor == ChessPiece.PieceColor.Light)
                {
                    piecesLight.AddLast(pieceOnNewSquare);
                }
                else
                {
                    piecesDark.AddLast(pieceOnNewSquare);
                }
            }

            string pos2 = BoardToString();
            if (pos1.Equals(pos2) == false)
            {
                int breakme = 0;
            }

            return !kingAttackedInNewPosition;
        }

        private LinkedList<Point> GetValidMoves(ChessPiece piece)
        {
            LinkedList<Point> squares = new LinkedList<Point>();

            if (1 == 1)
            {
                string FEN = GetFEN();
                LinkedList<string> moves = moveGeneratorInterface.getMoves(FEN);

                //foreach(string move in moves)
                //{
                //    Console.WriteLine(move);
                //}
                //Console.WriteLine("----");

                foreach (string move in moves)
                {
                    int xs = (int)char.GetNumericValue(move, 0);
                    if (char.GetNumericValue(move, 0) == (piece.Xindex) && char.GetNumericValue(move, 1) == (piece.Yindex))
                    {
                        squares.AddLast(new Point((int)char.GetNumericValue(move, 2), (int)char.GetNumericValue(move, 3)));
                    }
                }

                foreach (Point p in squares)
                {

                }

                return squares;
            }

            // this is now unreachable

            if (piece.pieceType == ChessPiece.PieceType.Pawn)
            {
                if (piece.pieceColor == ChessPiece.PieceColor.Light)
                {
                    // Forward
                    if ((piece.Yindex < 7 && playingField[piece.Xindex, piece.Yindex + 1] == null)/* && SimulatedMoveOK(piece, new Point(piece.Xindex, piece.Yindex + 1))*/)
                    {
                        squares.AddLast(new Point(piece.Xindex, piece.Yindex + 1));

                        // Forward at starting position
                        if (piece.Yindex == 1 && playingField[piece.Xindex, piece.Yindex + 2] == null)
                        {
                            squares.AddLast(new Point(piece.Xindex, piece.Yindex + 2));
                        }
                    }

                    // Take left
                    if ((piece.Xindex > 0 && piece.Yindex < 7 && playingField[piece.Xindex - 1, piece.Yindex + 1] != null && playingField[piece.Xindex - 1, piece.Yindex + 1].pieceColor != piece.pieceColor)/* && SimulatedMoveOK(piece, new Point(piece.Xindex - 1, piece.Yindex + 1))*/)
                    {
                        squares.AddLast(new Point(piece.Xindex - 1, piece.Yindex + 1));
                    }

                    // Take right
                    if ((piece.Xindex < 7 && piece.Yindex < 7 && playingField[piece.Xindex + 1, piece.Yindex + 1] != null && playingField[piece.Xindex + 1, piece.Yindex + 1].pieceColor != piece.pieceColor)/* && SimulatedMoveOK(piece, new Point(piece.Xindex + 1, piece.Yindex + 1))*/)
                    {
                        squares.AddLast(new Point(piece.Xindex + 1, piece.Yindex + 1));
                    }
                }
                else if (piece.pieceColor == ChessPiece.PieceColor.Dark)
                {
                    if (piece.Yindex > 0 && playingField[piece.Xindex, piece.Yindex - 1] == null)
                    {
                        squares.AddLast(new Point(piece.Xindex, piece.Yindex - 1));

                        if (piece.Yindex == 6 && playingField[piece.Xindex, piece.Yindex - 2] == null)
                        {
                            squares.AddLast(new Point(piece.Xindex, piece.Yindex - 2));
                        }
                    }

                    if (piece.Xindex > 0 && piece.Yindex > 0 && playingField[piece.Xindex - 1, piece.Yindex - 1] != null && playingField[piece.Xindex - 1, piece.Yindex - 1].pieceColor != piece.pieceColor)
                    {
                        squares.AddLast(new Point(piece.Xindex - 1, piece.Yindex - 1));
                    }

                    if (piece.Xindex < 7 && piece.Yindex > 0 && playingField[piece.Xindex + 1, piece.Yindex - 1] != null && playingField[piece.Xindex + 1, piece.Yindex - 1].pieceColor != piece.pieceColor)
                    {
                        squares.AddLast(new Point(piece.Xindex + 1, piece.Yindex - 1));
                    }
                }
            }
            else if (piece.pieceType == ChessPiece.PieceType.Knight)
            {
                if (piece.Xindex > 1 && piece.Yindex < 7 && (playingField[piece.Xindex - 2, piece.Yindex + 1] == null || (playingField[piece.Xindex - 2, piece.Yindex + 1] != null && playingField[piece.Xindex - 2, piece.Yindex + 1].pieceColor != piece.pieceColor)))
                {
                    squares.AddLast(new Point(piece.Xindex - 2, piece.Yindex + 1));
                }
                if (piece.Xindex > 0 && piece.Yindex < 6 && (playingField[piece.Xindex - 1, piece.Yindex + 2] == null || (playingField[piece.Xindex - 1, piece.Yindex + 2] != null && playingField[piece.Xindex - 1, piece.Yindex + 2].pieceColor != piece.pieceColor)))
                {
                    squares.AddLast(new Point(piece.Xindex - 1, piece.Yindex + 2));
                }

                if (piece.Xindex < 6 && piece.Yindex > 0 && (playingField[piece.Xindex + 2, piece.Yindex - 1] == null || (playingField[piece.Xindex + 2, piece.Yindex - 1] != null && playingField[piece.Xindex + 2, piece.Yindex - 1].pieceColor != piece.pieceColor)))
                {
                    squares.AddLast(new Point(piece.Xindex + 2, piece.Yindex - 1));
                }
                if (piece.Xindex < 7 && piece.Yindex > 1 && (playingField[piece.Xindex + 1, piece.Yindex - 2] == null || (playingField[piece.Xindex + 1, piece.Yindex - 2] != null && playingField[piece.Xindex + 1, piece.Yindex - 2].pieceColor != piece.pieceColor)))
                {
                    squares.AddLast(new Point(piece.Xindex + 1, piece.Yindex - 2));
                }

                if (piece.Xindex > 1 && piece.Yindex > 0 && (playingField[piece.Xindex - 2, piece.Yindex - 1] == null || (playingField[piece.Xindex - 2, piece.Yindex - 1] != null && playingField[piece.Xindex - 2, piece.Yindex - 1].pieceColor != piece.pieceColor)))
                {
                    squares.AddLast(new Point(piece.Xindex - 2, piece.Yindex - 1));
                }
                if (piece.Xindex > 0 && piece.Yindex > 1 && (playingField[piece.Xindex - 1, piece.Yindex - 2] == null || (playingField[piece.Xindex - 1, piece.Yindex - 2] != null && playingField[piece.Xindex - 1, piece.Yindex - 2].pieceColor != piece.pieceColor)))
                {
                    squares.AddLast(new Point(piece.Xindex - 1, piece.Yindex - 2));
                }

                if (piece.Xindex < 6 && piece.Yindex < 7 && (playingField[piece.Xindex + 2, piece.Yindex + 1] == null || (playingField[piece.Xindex + 2, piece.Yindex + 1] != null && playingField[piece.Xindex + 2, piece.Yindex + 1].pieceColor != piece.pieceColor)))
                {
                    squares.AddLast(new Point(piece.Xindex + 2, piece.Yindex + 1));
                }
                if (piece.Xindex < 7 && piece.Yindex < 6 && (playingField[piece.Xindex + 1, piece.Yindex + 2] == null || (playingField[piece.Xindex + 1, piece.Yindex + 2] != null && playingField[piece.Xindex + 1, piece.Yindex + 2].pieceColor != piece.pieceColor)))
                {
                    squares.AddLast(new Point(piece.Xindex + 1, piece.Yindex + 2));
                }
            }
            else if (piece.pieceType == ChessPiece.PieceType.Rook)
            {
                // Up
                for (int i = piece.Yindex + 1; i < 8; i++)
                {
                    if (playingField[piece.Xindex, i] == null || (playingField[piece.Xindex, i] != null && playingField[piece.Xindex, i].pieceColor != piece.pieceColor))
                    {
                        squares.AddLast(new Point(piece.Xindex, i));
                        if (playingField[piece.Xindex, i] != null)
                        {
                            break;
                        }
                    }
                    else
                    {
                        break;
                    }
                }

                // Down
                for (int i = piece.Yindex - 1; i > -1; i--)
                {
                    if (playingField[piece.Xindex, i] == null || (playingField[piece.Xindex, i] != null && playingField[piece.Xindex, i].pieceColor != piece.pieceColor))
                    {
                        squares.AddLast(new Point(piece.Xindex, i));
                        if (playingField[piece.Xindex, i] != null)
                        {
                            break;
                        }
                    }
                    else
                    {
                        break;
                    }
                }

                // Left
                for (int i = piece.Xindex - 1; i > -1; i--)
                {
                    if (playingField[i, piece.Yindex] == null || (playingField[i, piece.Yindex] != null && playingField[i, piece.Yindex].pieceColor != piece.pieceColor))
                    {
                        squares.AddLast(new Point(i, piece.Yindex));
                        if (playingField[i, piece.Yindex] != null)
                        {
                            break;
                        }
                    }
                    else
                    {
                        break;
                    }
                }

                // Right
                for (int i = piece.Xindex + 1; i < 8; i++)
                {
                    if (playingField[i, piece.Yindex] == null || (playingField[i, piece.Yindex] != null && playingField[i, piece.Yindex].pieceColor != piece.pieceColor))
                    {
                        squares.AddLast(new Point(i, piece.Yindex));
                        if (playingField[i, piece.Yindex] != null)
                        {
                            break;
                        }
                    }
                    else
                    {
                        break;
                    }
                }
            }
            else if (piece.pieceType == ChessPiece.PieceType.Bishop)
            {
                // Up left
                for (int i = 1; piece.Xindex - i > -1 && piece.Yindex + i < 8; i++)
                {
                    if (playingField[piece.Xindex - i, piece.Yindex + i] == null || (playingField[piece.Xindex - i, piece.Yindex + i] != null && playingField[piece.Xindex - i, piece.Yindex + i].pieceColor != piece.pieceColor))
                    {
                        squares.AddLast(new Point(piece.Xindex - i, piece.Yindex + i));
                        if (playingField[piece.Xindex - i, piece.Yindex + i] != null)
                        {
                            break;
                        }
                    }
                    else
                    {
                        break;
                    }
                }

                // Up right
                for (int i = 1; piece.Xindex + i < 8 && piece.Yindex + i < 8; i++)
                {
                    if (playingField[piece.Xindex + i, piece.Yindex + i] == null || (playingField[piece.Xindex + i, piece.Yindex + i] != null && playingField[piece.Xindex + i, piece.Yindex + i].pieceColor != piece.pieceColor))
                    {
                        squares.AddLast(new Point(piece.Xindex + i, piece.Yindex + i));
                        if (playingField[piece.Xindex + i, piece.Yindex + i] != null)
                        {
                            break;
                        }
                    }
                    else
                    {
                        break;
                    }
                }

                // Down left
                for (int i = 1; piece.Xindex - i > -1 && piece.Yindex - i > -1; i++)
                {
                    if (playingField[piece.Xindex - i, piece.Yindex - i] == null || (playingField[piece.Xindex - i, piece.Yindex - i] != null && playingField[piece.Xindex - i, piece.Yindex - i].pieceColor != piece.pieceColor))
                    {
                        squares.AddLast(new Point(piece.Xindex - i, piece.Yindex - i));
                        if (playingField[piece.Xindex - i, piece.Yindex - i] != null)
                        {
                            break;
                        }
                    }
                    else
                    {
                        break;
                    }
                }

                // Down right
                for (int i = 1; piece.Xindex + i < 8 && piece.Yindex - i > -1; i++)
                {
                    if (playingField[piece.Xindex + i, piece.Yindex - i] == null || (playingField[piece.Xindex + i, piece.Yindex - i] != null && playingField[piece.Xindex + i, piece.Yindex - i].pieceColor != piece.pieceColor))
                    {
                        squares.AddLast(new Point(piece.Xindex + i, piece.Yindex - i));
                        if (playingField[piece.Xindex + i, piece.Yindex - i] != null)
                        {
                            break;
                        }
                    }
                    else
                    {
                        break;
                    }
                }
            }
            else if (piece.pieceType == ChessPiece.PieceType.Queen)
            {
                // Queen = Bishop + Rook

                // Up
                for (int i = piece.Yindex + 1; i < 8; i++)
                {
                    if (playingField[piece.Xindex, i] == null || (playingField[piece.Xindex, i] != null && playingField[piece.Xindex, i].pieceColor != piece.pieceColor))
                    {
                        squares.AddLast(new Point(piece.Xindex, i));
                        if (playingField[piece.Xindex, i] != null)
                        {
                            break;
                        }
                    }
                    else
                    {
                        break;
                    }
                }

                // Down
                for (int i = piece.Yindex - 1; i > -1; i--)
                {
                    if (playingField[piece.Xindex, i] == null || (playingField[piece.Xindex, i] != null && playingField[piece.Xindex, i].pieceColor != piece.pieceColor))
                    {
                        squares.AddLast(new Point(piece.Xindex, i));
                        if (playingField[piece.Xindex, i] != null)
                        {
                            break;
                        }
                    }
                    else
                    {
                        break;
                    }
                }

                // Left
                for (int i = piece.Xindex - 1; i > -1; i--)
                {
                    if (playingField[i, piece.Yindex] == null || (playingField[i, piece.Yindex] != null && playingField[i, piece.Yindex].pieceColor != piece.pieceColor))
                    {
                        squares.AddLast(new Point(i, piece.Yindex));
                        if (playingField[i, piece.Yindex] != null)
                        {
                            break;
                        }
                    }
                    else
                    {
                        break;
                    }
                }

                // Right
                for (int i = piece.Xindex + 1; i < 8; i++)
                {
                    if (playingField[i, piece.Yindex] == null || (playingField[i, piece.Yindex] != null && playingField[i, piece.Yindex].pieceColor != piece.pieceColor))
                    {
                        squares.AddLast(new Point(i, piece.Yindex));
                        if (playingField[i, piece.Yindex] != null)
                        {
                            break;
                        }
                    }
                    else
                    {
                        break;
                    }
                }

                // Up left
                for (int i = 1; piece.Xindex - i > -1 && piece.Yindex + i < 8; i++)
                {
                    if (playingField[piece.Xindex - i, piece.Yindex + i] == null || (playingField[piece.Xindex - i, piece.Yindex + i] != null && playingField[piece.Xindex - i, piece.Yindex + i].pieceColor != piece.pieceColor))
                    {
                        squares.AddLast(new Point(piece.Xindex - i, piece.Yindex + i));
                        if (playingField[piece.Xindex - i, piece.Yindex + i] != null)
                        {
                            break;
                        }
                    }
                    else
                    {
                        break;
                    }
                }

                // Up right
                for (int i = 1; piece.Xindex + i < 8 && piece.Yindex + i < 8; i++)
                {
                    if (playingField[piece.Xindex + i, piece.Yindex + i] == null || (playingField[piece.Xindex + i, piece.Yindex + i] != null && playingField[piece.Xindex + i, piece.Yindex + i].pieceColor != piece.pieceColor))
                    {
                        squares.AddLast(new Point(piece.Xindex + i, piece.Yindex + i));
                        if (playingField[piece.Xindex + i, piece.Yindex + i] != null)
                        {
                            break;
                        }
                    }
                    else
                    {
                        break;
                    }
                }

                // Down left
                for (int i = 1; piece.Xindex - i > -1 && piece.Yindex - i > -1; i++)
                {
                    if (playingField[piece.Xindex - i, piece.Yindex - i] == null || (playingField[piece.Xindex - i, piece.Yindex - i] != null && playingField[piece.Xindex - i, piece.Yindex - i].pieceColor != piece.pieceColor))
                    {
                        squares.AddLast(new Point(piece.Xindex - i, piece.Yindex - i));
                        if (playingField[piece.Xindex - i, piece.Yindex - i] != null)
                        {
                            break;
                        }
                    }
                    else
                    {
                        break;
                    }
                }

                // Down right
                for (int i = 1; piece.Xindex + i < 8 && piece.Yindex - i > -1; i++)
                {
                    if (playingField[piece.Xindex + i, piece.Yindex - i] == null || (playingField[piece.Xindex + i, piece.Yindex - i] != null && playingField[piece.Xindex + i, piece.Yindex - i].pieceColor != piece.pieceColor))
                    {
                        squares.AddLast(new Point(piece.Xindex + i, piece.Yindex - i));
                        if (playingField[piece.Xindex + i, piece.Yindex - i] != null)
                        {
                            break;
                        }
                    }
                    else
                    {
                        break;
                    }
                }
            }
            else if (piece.pieceType == ChessPiece.PieceType.King)
            {
                // 1 move queen

                // Up
                for (int i = piece.Yindex + 1; i < 8; i++)
                {
                    if ((playingField[piece.Xindex, i] == null || (playingField[piece.Xindex, i] != null && playingField[piece.Xindex, i].pieceColor != piece.pieceColor)) && SquareAttacked(new Point(piece.Xindex, i), piece.pieceColor) == false)
                    {
                        squares.AddLast(new Point(piece.Xindex, i));
                    }
                    break;
                }

                // Down
                for (int i = piece.Yindex - 1; i > -1; i--)
                {
                    if ((playingField[piece.Xindex, i] == null || (playingField[piece.Xindex, i] != null && playingField[piece.Xindex, i].pieceColor != piece.pieceColor)) && SquareAttacked(new Point(piece.Xindex, i), piece.pieceColor) == false)
                    {
                        squares.AddLast(new Point(piece.Xindex, i));
                    }
                    break;
                }

                // Left
                for (int i = piece.Xindex - 1; i > -1; i--)
                {
                    if ((playingField[i, piece.Yindex] == null || (playingField[i, piece.Yindex] != null && playingField[i, piece.Yindex].pieceColor != piece.pieceColor)) && SquareAttacked(new Point(i, piece.Yindex), piece.pieceColor) == false)
                    {
                        squares.AddLast(new Point(i, piece.Yindex));
                    }
                    break;
                }

                // Right
                for (int i = piece.Xindex + 1; i < 8; i++)
                {
                    if ((playingField[i, piece.Yindex] == null || (playingField[i, piece.Yindex] != null && playingField[i, piece.Yindex].pieceColor != piece.pieceColor)) && SquareAttacked(new Point(i, piece.Yindex), piece.pieceColor) == false)
                    {
                        squares.AddLast(new Point(i, piece.Yindex));
                    }
                    break;
                }

                // Up left
                for (int i = 1; piece.Xindex - i > -1 && piece.Yindex + i < 8; i++)
                {
                    if ((playingField[piece.Xindex - i, piece.Yindex + i] == null || (playingField[piece.Xindex - i, piece.Yindex + i] != null && playingField[piece.Xindex - i, piece.Yindex + i].pieceColor != piece.pieceColor)) && SquareAttacked(new Point(piece.Xindex - i, piece.Yindex + i), piece.pieceColor) == false)
                    {
                        squares.AddLast(new Point(piece.Xindex - i, piece.Yindex + i));
                    }
                    break;
                }

                // Up right
                for (int i = 1; piece.Xindex + i < 8 && piece.Yindex + i < 8; i++)
                {
                    if ((playingField[piece.Xindex + i, piece.Yindex + i] == null || (playingField[piece.Xindex + i, piece.Yindex + i] != null && playingField[piece.Xindex + i, piece.Yindex + i].pieceColor != piece.pieceColor)) && SquareAttacked(new Point(piece.Xindex + i, piece.Yindex + i), piece.pieceColor) == false)
                    {
                        squares.AddLast(new Point(piece.Xindex + i, piece.Yindex + i));
                    }
                    break;
                }

                // Down left
                for (int i = 1; piece.Xindex - i > -1 && piece.Yindex - i > -1; i++)
                {
                    if ((playingField[piece.Xindex - i, piece.Yindex - i] == null || (playingField[piece.Xindex - i, piece.Yindex - i] != null && playingField[piece.Xindex - i, piece.Yindex - i].pieceColor != piece.pieceColor)) && SquareAttacked(new Point(piece.Xindex - i, piece.Yindex - i), piece.pieceColor) == false)
                    {
                        squares.AddLast(new Point(piece.Xindex - i, piece.Yindex - i));
                    }
                    break;
                }

                // Down right
                for (int i = 1; piece.Xindex + i < 8 && piece.Yindex - i > -1; i++)
                {
                    if ((playingField[piece.Xindex + i, piece.Yindex - i] == null || (playingField[piece.Xindex + i, piece.Yindex - i] != null && playingField[piece.Xindex + i, piece.Yindex - i].pieceColor != piece.pieceColor)) && SquareAttacked(new Point(piece.Xindex + i, piece.Yindex - i), piece.pieceColor) == false)
                    {
                        squares.AddLast(new Point(piece.Xindex + i, piece.Yindex - i));
                    }
                    break;
                }
            }

            // Check for pins???
            LinkedList<Point> squaresFinal = new LinkedList<Point>();
            foreach (Point p in squares)
            {
                if (SimulatedMoveOK(piece, p) &&
                    (
                        (
                            playingField[p.X, p.Y] != null &&
                            playingField[p.X, p.Y].pieceType != ChessPiece.PieceType.King
                        ) ||
                            playingField[p.X, p.Y] == null
                    )
                  )
                {
                    squaresFinal.AddLast(p);
                }
            }

            return squaresFinal;
        }

        private LinkedList<Point> GetAllValidMoves(ChessPiece.PieceColor piecesColor)
        {
            LinkedList<Point> validMoves = new LinkedList<Point>();

            if (piecesColor == ChessPiece.PieceColor.Light)
            {
                foreach (ChessPiece c in piecesLight)
                {
                    LinkedList<Point> pieceMoves = GetValidMoves(c);
                    foreach (Point p in pieceMoves)
                    {
                        validMoves.AddLast(p);
                    }
                }
            }
            else if (piecesColor == ChessPiece.PieceColor.Dark)
            {
                foreach (ChessPiece c in piecesDark)
                {
                    LinkedList<Point> pieceMoves = GetValidMoves(c);
                    foreach (Point p in pieceMoves)
                    {
                        validMoves.AddLast(p);
                    }
                }
            }

            return validMoves;
        }

        public string BoardToString()
        {
            StringBuilder sb = new StringBuilder();
            for (int i = 0; i < playingField.GetLength(0); i++) // columns
            {
                for (int j = 0; j < playingField.GetLength(1); j++) // rows
                {
                    int x = j;
                    int y = i;
                    if (facingLight)
                    {
                        x = (x * -1 + 7);
                        y = (y * -1 + 7);
                    }
                    ChessPiece atSquare = playingField[x, y];
                    if (atSquare == null)
                    {
                        sb.Append("□");
                    }
                    else
                    {
                        sb.Append(atSquare.ToString());
                    }
                }
                sb.Append(Environment.NewLine);
            }
            return sb.ToString();
        }

        private void PositionStandard()
        {
            // Light
            piecesLight.AddLast(new ChessPiece(0, 0, ChessPiece.PieceType.Rook, ChessPiece.PieceColor.Light));
            piecesLight.AddLast(new ChessPiece(1, 0, ChessPiece.PieceType.Knight, ChessPiece.PieceColor.Light));
            piecesLight.AddLast(new ChessPiece(2, 0, ChessPiece.PieceType.Bishop, ChessPiece.PieceColor.Light));
            piecesLight.AddLast(new ChessPiece(4, 0, ChessPiece.PieceType.Queen, ChessPiece.PieceColor.Light));
            piecesLight.AddLast(new ChessPiece(3, 0, ChessPiece.PieceType.King, ChessPiece.PieceColor.Light));
            kingLight = piecesLight.Last.Value;
            piecesLight.AddLast(new ChessPiece(5, 0, ChessPiece.PieceType.Bishop, ChessPiece.PieceColor.Light));
            piecesLight.AddLast(new ChessPiece(6, 0, ChessPiece.PieceType.Knight, ChessPiece.PieceColor.Light));
            piecesLight.AddLast(new ChessPiece(7, 0, ChessPiece.PieceType.Rook, ChessPiece.PieceColor.Light));
            piecesLight.AddLast(new ChessPiece(0, 1, ChessPiece.PieceType.Pawn, ChessPiece.PieceColor.Light));
            piecesLight.AddLast(new ChessPiece(1, 1, ChessPiece.PieceType.Pawn, ChessPiece.PieceColor.Light));
            piecesLight.AddLast(new ChessPiece(2, 1, ChessPiece.PieceType.Pawn, ChessPiece.PieceColor.Light));
            piecesLight.AddLast(new ChessPiece(3, 1, ChessPiece.PieceType.Pawn, ChessPiece.PieceColor.Light));
            piecesLight.AddLast(new ChessPiece(4, 1, ChessPiece.PieceType.Pawn, ChessPiece.PieceColor.Light));
            piecesLight.AddLast(new ChessPiece(5, 1, ChessPiece.PieceType.Pawn, ChessPiece.PieceColor.Light));
            piecesLight.AddLast(new ChessPiece(6, 1, ChessPiece.PieceType.Pawn, ChessPiece.PieceColor.Light));
            piecesLight.AddLast(new ChessPiece(7, 1, ChessPiece.PieceType.Pawn, ChessPiece.PieceColor.Light));

            // Dark
            piecesDark.AddLast(new ChessPiece(0, 7, ChessPiece.PieceType.Rook, ChessPiece.PieceColor.Dark));
            piecesDark.AddLast(new ChessPiece(1, 7, ChessPiece.PieceType.Knight, ChessPiece.PieceColor.Dark));
            piecesDark.AddLast(new ChessPiece(2, 7, ChessPiece.PieceType.Bishop, ChessPiece.PieceColor.Dark));
            piecesDark.AddLast(new ChessPiece(4, 7, ChessPiece.PieceType.Queen, ChessPiece.PieceColor.Dark));
            piecesDark.AddLast(new ChessPiece(3, 7, ChessPiece.PieceType.King, ChessPiece.PieceColor.Dark));
            kingDark = piecesDark.Last.Value;
            piecesDark.AddLast(new ChessPiece(5, 7, ChessPiece.PieceType.Bishop, ChessPiece.PieceColor.Dark));
            piecesDark.AddLast(new ChessPiece(6, 7, ChessPiece.PieceType.Knight, ChessPiece.PieceColor.Dark));
            piecesDark.AddLast(new ChessPiece(7, 7, ChessPiece.PieceType.Rook, ChessPiece.PieceColor.Dark));
            piecesDark.AddLast(new ChessPiece(0, 6, ChessPiece.PieceType.Pawn, ChessPiece.PieceColor.Dark));
            piecesDark.AddLast(new ChessPiece(1, 6, ChessPiece.PieceType.Pawn, ChessPiece.PieceColor.Dark));
            piecesDark.AddLast(new ChessPiece(2, 6, ChessPiece.PieceType.Pawn, ChessPiece.PieceColor.Dark));
            piecesDark.AddLast(new ChessPiece(3, 6, ChessPiece.PieceType.Pawn, ChessPiece.PieceColor.Dark));
            piecesDark.AddLast(new ChessPiece(4, 6, ChessPiece.PieceType.Pawn, ChessPiece.PieceColor.Dark));
            piecesDark.AddLast(new ChessPiece(5, 6, ChessPiece.PieceType.Pawn, ChessPiece.PieceColor.Dark));
            piecesDark.AddLast(new ChessPiece(6, 6, ChessPiece.PieceType.Pawn, ChessPiece.PieceColor.Dark));
            piecesDark.AddLast(new ChessPiece(7, 6, ChessPiece.PieceType.Pawn, ChessPiece.PieceColor.Dark));
        }

        private void PositionDebug1()
        {
            // Light
            piecesLight.AddLast(new ChessPiece(0, 0, ChessPiece.PieceType.Rook, ChessPiece.PieceColor.Light));
            piecesLight.AddLast(new ChessPiece(4, 2, ChessPiece.PieceType.Knight, ChessPiece.PieceColor.Light));
            piecesLight.AddLast(new ChessPiece(5, 2, ChessPiece.PieceType.Knight, ChessPiece.PieceColor.Light));
            piecesLight.AddLast(new ChessPiece(3, 1, ChessPiece.PieceType.Bishop, ChessPiece.PieceColor.Light));
            piecesLight.AddLast(new ChessPiece(3, 4, ChessPiece.PieceType.Queen, ChessPiece.PieceColor.Light));
            piecesLight.AddLast(new ChessPiece(4, 0, ChessPiece.PieceType.King, ChessPiece.PieceColor.Light));
            kingLight = piecesLight.Last.Value;
            piecesLight.AddLast(new ChessPiece(7, 0, ChessPiece.PieceType.Rook, ChessPiece.PieceColor.Light));
            piecesLight.AddLast(new ChessPiece(0, 5, ChessPiece.PieceType.Pawn, ChessPiece.PieceColor.Light));
            piecesLight.AddLast(new ChessPiece(2, 5, ChessPiece.PieceType.Pawn, ChessPiece.PieceColor.Light));
            piecesLight.AddLast(new ChessPiece(5, 1, ChessPiece.PieceType.Pawn, ChessPiece.PieceColor.Light));
            piecesLight.AddLast(new ChessPiece(6, 2, ChessPiece.PieceType.Pawn, ChessPiece.PieceColor.Light));
            piecesLight.AddLast(new ChessPiece(7, 1, ChessPiece.PieceType.Pawn, ChessPiece.PieceColor.Light));

            // Dark
            piecesDark.AddLast(new ChessPiece(4, 6, ChessPiece.PieceType.Bishop, ChessPiece.PieceColor.Dark));
            piecesDark.AddLast(new ChessPiece(1, 7, ChessPiece.PieceType.Queen, ChessPiece.PieceColor.Dark));
            piecesDark.AddLast(new ChessPiece(0, 7, ChessPiece.PieceType.King, ChessPiece.PieceColor.Dark));
            kingDark = piecesDark.Last.Value;
            piecesDark.AddLast(new ChessPiece(6, 7, ChessPiece.PieceType.Knight, ChessPiece.PieceColor.Dark));
            piecesDark.AddLast(new ChessPiece(7, 7, ChessPiece.PieceType.Rook, ChessPiece.PieceColor.Dark));
            piecesDark.AddLast(new ChessPiece(0, 6, ChessPiece.PieceType.Pawn, ChessPiece.PieceColor.Dark));
            piecesDark.AddLast(new ChessPiece(5, 5, ChessPiece.PieceType.Pawn, ChessPiece.PieceColor.Dark));
            piecesDark.AddLast(new ChessPiece(6, 6, ChessPiece.PieceType.Pawn, ChessPiece.PieceColor.Dark));
            piecesDark.AddLast(new ChessPiece(7, 6, ChessPiece.PieceType.Pawn, ChessPiece.PieceColor.Dark));
        }

        // Check for check mate appetite
        private void PositionDebug2()
        {
            // Light
            piecesLight.AddLast(new ChessPiece(0, 1, ChessPiece.PieceType.Pawn, ChessPiece.PieceColor.Light));
            piecesLight.AddLast(new ChessPiece(1, 1, ChessPiece.PieceType.Pawn, ChessPiece.PieceColor.Light));
            piecesLight.AddLast(new ChessPiece(2, 1, ChessPiece.PieceType.Pawn, ChessPiece.PieceColor.Light));
            piecesLight.AddLast(new ChessPiece(6, 2, ChessPiece.PieceType.Bishop, ChessPiece.PieceColor.Light));
            piecesLight.AddLast(new ChessPiece(1, 0, ChessPiece.PieceType.King, ChessPiece.PieceColor.Light));
            kingLight = piecesLight.Last.Value;

            // Dark
            piecesDark.AddLast(new ChessPiece(4, 6, ChessPiece.PieceType.Bishop, ChessPiece.PieceColor.Dark));
            piecesDark.AddLast(new ChessPiece(3, 3, ChessPiece.PieceType.Queen, ChessPiece.PieceColor.Dark));
            piecesDark.AddLast(new ChessPiece(0, 7, ChessPiece.PieceType.King, ChessPiece.PieceColor.Dark));
            kingDark = piecesDark.Last.Value;
        }

        public bool SetUpBoard(string FEN)
        {
            return true;
        }

        public string GetFEN()
        {
            StringBuilder FEN = new StringBuilder();

            // Pieces
            int emptySquareCounter = 0;
            for (int i = 0; i < playingField.GetLength(0); i++) // columns
            {
                for (int j = 0; j < playingField.GetLength(1); j++) // rows
                {
                    int x = j;
                    int y = i;
                    //if (facingLight)
                    //{
                    x = (x * -1 + 7);
                    y = (y * -1 + 7);
                    //}
                    ChessPiece atSquare = playingField[x, y];

                    if (atSquare == null)
                    {
                        emptySquareCounter += 1;
                    }
                    else
                    {
                        if(emptySquareCounter != 0)
                        {
                            FEN.Append(emptySquareCounter.ToString());
                        }
                        FEN.Append(atSquare.ToString());

                        emptySquareCounter = 0;
                    }
                }
                if (emptySquareCounter != 0)
                {
                    FEN.Append(emptySquareCounter.ToString());
                }
                if (i < playingField.GetLength(0) - 1)
                {
                    FEN.Append("/");
                }
                emptySquareCounter = 0;
            }

            // Color
            if (lightTurn)
            {
                FEN.Append(" w");
            }
            else
            {
                FEN.Append(" b");
            }

            return FEN.ToString();
        }

        public void SetUpBoard()
        {
            piecesLight = new LinkedList<ChessPiece>();
            //takenLight = new LinkedList<ChessPiece>();
            piecesDark = new LinkedList<ChessPiece>();
            //takenDark = new LinkedList<ChessPiece>();
            playingField = new ChessPiece[8, 8];
            mouseDown = false;
            piecePickedValidMoves = new LinkedList<Point>();
            lightTurn = true;
            facingLight = true;
            piecePicked = null;
            oldSquareLight = new Point(-1, -1);
            oldSquareDark = new Point(-1, -1);

            // Position set up
            PositionStandard();
            //PositionDebug1();
            //PositionDebug2();

            // Light
            foreach (ChessPiece c in piecesLight)
            {
                playingField[c.Xindex, c.Yindex] = c;
            }

            // Dark
            foreach (ChessPiece c in piecesDark)
            {
                playingField[c.Xindex, c.Yindex] = c;
            }

            Invalidate();

            //string FEN = GetFEN();
            //int breakme = 0;
        }

        private void MovePiece(ChessPiece piece, int newX, int newY)
        {
            if (playingField[newX, newY] != null)
            {
                if (playingField[newX, newY].pieceColor == ChessPiece.PieceColor.Light)
                {
                    piecesLight.Remove(playingField[newX, newY]);
                    //takenLight.AddLast(playingField[newX, newY]);
                }
                else if (playingField[newX, newY].pieceColor == ChessPiece.PieceColor.Dark)
                {
                    piecesDark.Remove(playingField[newX, newY]);
                    //takenDark.AddLast(playingField[newX, newY]);
                }
            }
            if (piece.pieceType == ChessPiece.PieceType.Pawn && ((newY == 7 && piece.pieceColor == ChessPiece.PieceColor.Light) || (newY == 0 && piece.pieceColor == ChessPiece.PieceColor.Dark)))
            {
                // Autopromotion to a queen
                piece.pieceType = ChessPiece.PieceType.Queen;
            }

            playingField[piece.Xindex, piece.Yindex] = null;
            playingField[newX, newY] = piece;

            bool noMove = false;
            if (piece.Xindex == newX && piece.Yindex == newY)
            {
                noMove = true;
            }
            else
            {
                lightTurn = !lightTurn;
            }

            piece.Xindex = newX;
            piece.Yindex = newY;

            //LinkedList<Point> allValid = GetAllValidMoves(lightTurn ? ChessPiece.PieceColor.Light : ChessPiece.PieceColor.Dark);
            //if (allValid.Count == 0)
            //{
            //    SetUpBoard();
            //}

            if (noMove == false)
            {
                OnPieceMoved(this);
            }

            // "AI" thingy
            if (lightTurn == false)
            {
                Stopwatch sw = new Stopwatch();
                sw.Start();
                MiniMaxContext recommendedMove = MiniMax3(0, 3/*3*/, double.MinValue, double.MaxValue);
                sw.Stop();
                elapsedTime = sw.ElapsedMilliseconds;
                generatedPositions = new Dictionary<string, int>(); // Clear memory
                GC.Collect();
                if (recommendedMove.newLocation.X == -1 || recommendedMove.newLocation.Y == -1) // no moves available - stalemate or checkmate
                {
                    int breakme = 0;
                }
                else
                {
                    MovePiece(recommendedMove.piece, recommendedMove.newLocation.X, recommendedMove.newLocation.Y);
                }
            }
            piecePicked = null;
            piecePickedValidMoves = new LinkedList<Point>();
            Invalidate();
            Refresh();
        }
        public double elapsedTime = -1;

        // returns taken piece
        private ChessPiece JustMove(ChessPiece piece, int newX, int newY)
        {
            ChessPiece potentialTaken = playingField[newX, newY];
            if (playingField[newX, newY] != null)
            {
                if (playingField[newX, newY].pieceColor == ChessPiece.PieceColor.Light)
                {
                    piecesLight.Remove(playingField[newX, newY]);
                    //takenLight.AddLast(playingField[newX, newY]);
                }
                else if (playingField[newX, newY].pieceColor == ChessPiece.PieceColor.Dark)
                {
                    piecesDark.Remove(playingField[newX, newY]);
                    //takenDark.AddLast(playingField[newX, newY]);
                }
            }
            if (piece.pieceType == ChessPiece.PieceType.Pawn && ((newY == 7 && piece.pieceColor == ChessPiece.PieceColor.Light) || (newY == 0 && piece.pieceColor == ChessPiece.PieceColor.Dark)))
            {
                // Autopromotion to a queen
                piece.pieceType = ChessPiece.PieceType.Queen;
            }

            playingField[piece.Xindex, piece.Yindex] = null;
            playingField[newX, newY] = piece;

            piece.Xindex = newX;
            piece.Yindex = newY;

            return potentialTaken;
        }

        // Move event
        public event PieceMovedEventHandler PieceMoved;
        public delegate void PieceMovedEventHandler(Chessboard sender);
        private void OnPieceMoved(Chessboard sender)
        {
            PieceMoved?.Invoke(this);
        }

        private double GetPiecesValue(ChessPiece.PieceColor pieceColor)
        {
            double rez = 0;
            if (pieceColor == ChessPiece.PieceColor.Light)
            {
                foreach (ChessPiece p in piecesLight)
                {
                    rez += p.getPieceValue();
                }
            }
            else if (pieceColor == ChessPiece.PieceColor.Dark)
            {
                foreach (ChessPiece p in piecesDark)
                {
                    rez += p.getPieceValue();
                }
            }

            // Fourth iteration minimax
            //if (GetAllValidMoves(pieceColor).Count == 0 && KingAttacked(pieceColor))
            //{
            //    rez = -1000;
            //}

            return rez;
        }

        private double GetPiecesValue2(ChessPiece.PieceColor pieceColor)
        {
            double rez = 0;
            if (pieceColor == ChessPiece.PieceColor.Light)
            {
                foreach (ChessPiece p in piecesLight)
                {
                    rez += p.getPieceValue();
                }
            }
            else if (pieceColor == ChessPiece.PieceColor.Dark)
            {
                foreach (ChessPiece p in piecesDark)
                {
                    rez += p.getPieceValue();
                }
            }

            // Fourth iteration minimax
            if (GetAllValidMoves(pieceColor).Count == 0 && KingAttacked(pieceColor))
            {
                rez = -1000;
            }

            return rez;
        }

        // Score improved
        public event ScoreImprovedEventHandler ScoreImproved;
        public delegate void ScoreImprovedEventHandler(Chessboard sender, MiniMaxContext context);
        private void OnScoreImproved(Chessboard sender, MiniMaxContext context)
        {
            // COMMENT THIS OUT TO MAKE IT GO ZOOM
            ScoreImproved?.Invoke(this, context);
        }

        static string hashSHA256(string input, int len)
        {
            byte[] byteData = Encoding.UTF8.GetBytes(input);
            SHA256Managed hashed = new SHA256Managed();
            byte[] hashC = hashed.ComputeHash(byteData);
            byte[] hash = new byte[len];
            Array.ConstrainedCopy(hashC, 0, hash, 0, len);
            StringBuilder hashString = new StringBuilder();
            foreach (byte x in hash)
            {
                hashString.Append(String.Format("{0:x2}", x));
            }
            return hashString.ToString();
        }

        //static byte[] hashSHA256(string input, int len)
        //{
        //    byte[] byteData = Encoding.UTF8.GetBytes(input);
        //    SHA256Managed hashed = new SHA256Managed();
        //    byte[] hashC = hashed.ComputeHash(byteData);
        //    byte[] hash = new byte[len];
        //    Array.ConstrainedCopy(hashC, 0, hash, 0, len);
        //    return hash;
        //}

        Dictionary<string, int> generatedPositions;
        public int nodesCount;
        public int movesCount;
        // Third iteration
        private /*double*/MiniMaxContext MiniMax3(int depth, int maxDepth, double alpha, double beta)
        {
            if (depth == 0)
            {

                generatedPositions = new Dictionary<string, int>();
                nodesCount = 0;
                movesCount = 0;
            }
            nodesCount++;
            LinkedList<ChessPiece> pieces = new LinkedList<ChessPiece>(); // lightTurn ? piecesLight : piecesDark;
            if (lightTurn)
            {
                foreach (ChessPiece p in piecesLight)
                {
                    pieces.AddLast(p);
                }
            }
            else
            {
                foreach (ChessPiece p in piecesDark)
                {
                    pieces.AddLast(p);
                }
            }
            LinkedList<Point> pieceMoves;
            MiniMaxContext bestMoveContext = new MiniMaxContext();
            bestMoveContext.piece = null;
            bestMoveContext.scoreEval = double.MinValue;//depth % 2 == 0 ? double.MinValue : double.MaxValue;
            bestMoveContext.newLocation = new Point(-1, -1);
            LinkedList<Point> allValid = GetAllValidMoves(lightTurn ? ChessPiece.PieceColor.Light : ChessPiece.PieceColor.Dark);
            if (allValid.Count == 0 && KingAttacked(!lightTurn ? ChessPiece.PieceColor.Light : ChessPiece.PieceColor.Dark))
            {
                bestMoveContext.scoreEval = -1000;//depth % 2 == 0 ? 1000 : -1000;
                return bestMoveContext;
            }
            bool savedTurnLight = lightTurn;

            //string cbPre = BoardToString();
            int counter = 0;
            bool canBreak = false;
            foreach (ChessPiece p in pieces)
            {
                ChessPiece.PieceType pieceType = p.pieceType;
                //string cbInter2 = BoardToString();
                pieceMoves = GetValidMoves(p);
                //string cbInter1 = BoardToString();

                //Console.WriteLine(cbInter1 + Environment.NewLine);

                foreach (Point pt in pieceMoves)
                {
                    movesCount++;
                    // save previous setup
                    Point oldLocation = new Point(p.Xindex, p.Yindex);
                    ChessPiece pieceAtNewLoc = playingField[pt.X, pt.Y];
                    ChessPiece taken = JustMove(p, pt.X, pt.Y);

                    //double newEvalMy = -1;
                    //double newEvalOpponent = -1;
                    //newEvalMy = GetPiecesValue(lightTurn ? ChessPiece.PieceColor.Light : ChessPiece.PieceColor.Dark);
                    //newEvalOpponent = GetPiecesValue(lightTurn ? ChessPiece.PieceColor.Dark : ChessPiece.PieceColor.Light);
                    //double newEval = -1;
                    //newEval = newEvalMy - newEvalOpponent;
                    //string boardPosition = BoardToString();

                    //double minimaxEval = 0;
                    //if (depth < maxDepth && generatedPositions.ContainsKey(boardPosition) == false)
                    //{
                    //    generatedPositions[boardPosition] = depth;
                    //    lightTurn = ! lightTurn;
                    //    MiniMaxContext recommendedMove = MiniMax1(depth + 1, maxDepth, alpha, beta);
                    //    //if ((recommendedMove.scoreEval > bestMoveContext.scoreEval && depth % 2 == 0) || (recommendedMove.scoreEval < bestMoveContext.scoreEval && depth % 2 == 1))
                    //    //{
                    //    //    bestMoveContext.scoreEval = recommendedMove.scoreEval;
                    //    //    if (depth == 0)
                    //    //    {
                    //    //        OnScoreImproved(this, bestMoveContext);
                    //    //    }
                    //    //}
                    //    minimaxEval = recommendedMove.scoreEval;
                    //}

                    //if ((newEval > bestMoveContext.scoreEval && depth % 2 == 0) || (newEval < bestMoveContext.scoreEval && depth % 2 == 1))
                    //{
                    //    bestMoveContext.scoreEval = newEval;
                    //    bestMoveContext.newLocation = pt;
                    //    bestMoveContext.piece = p;

                    //    if (depth == 0)
                    //    {
                    //        OnScoreImproved(this, bestMoveContext);
                    //    }
                    //}

                    string boardPosition = BoardToString();
                    //string hashedPos = hashSHA256(boardPosition, 16);
                    int dictionaryDepth = int.MaxValue;
                    bool posInDict = generatedPositions.TryGetValue(boardPosition/*hashedPos*/, out dictionaryDepth);
                    double newEval = -1;
                    double minimaxEval = double.MinValue;
                    // for d1
                    if (depth == 0)
                    {
                        double newEvalMy = newEvalMy = GetPiecesValue(lightTurn ? ChessPiece.PieceColor.Light : ChessPiece.PieceColor.Dark);
                        double newEvalOpponent = GetPiecesValue(lightTurn ? ChessPiece.PieceColor.Dark : ChessPiece.PieceColor.Light);
                        newEval = newEvalMy - newEvalOpponent;
                    }
                    if (depth < maxDepth)
                    {
                        if (posInDict && depth >= dictionaryDepth) // update anyway
                        {
                            if (depth == 0)
                            {
                                int breakme = 0;
                            }
                            double newEvalMy = newEvalMy = GetPiecesValue(lightTurn ? ChessPiece.PieceColor.Light : ChessPiece.PieceColor.Dark);
                            double newEvalOpponent = GetPiecesValue(lightTurn ? ChessPiece.PieceColor.Dark : ChessPiece.PieceColor.Light);
                            newEval = newEvalMy - newEvalOpponent;
                        }
                        else // try searching deeper
                        {
                            lightTurn = !lightTurn;

                            MiniMaxContext recommendedMove = MiniMax3(depth + 1, maxDepth, alpha, beta);
                            if (recommendedMove.scoreEval == -1000)
                            {
                                bestMoveContext.scoreEval = 1000;
                                bestMoveContext.newLocation = pt;
                                bestMoveContext.piece = p;
                                if (depth == 0)
                                {
                                    OnScoreImproved(this, bestMoveContext);
                                }
                            }
                            if (recommendedMove.newLocation.X == -1 || recommendedMove.newLocation.Y == -1)
                            {
                                double newEvalMy = newEvalMy = GetPiecesValue(lightTurn ? ChessPiece.PieceColor.Light : ChessPiece.PieceColor.Dark);
                                double newEvalOpponent = GetPiecesValue(lightTurn ? ChessPiece.PieceColor.Dark : ChessPiece.PieceColor.Light);
                                newEval = newEvalMy - newEvalOpponent;
                            }
                            else
                            {
                                minimaxEval = recommendedMove.scoreEval * -1;
                                newEval = minimaxEval;
                            }

                            lightTurn = !lightTurn;
                        }
                    }
                    else // is a leaf - set the move anyway
                    {
                        if (depth == 0)
                        {
                            int breakme = 0;
                        }
                        double newEvalMy = newEvalMy = GetPiecesValue(lightTurn ? ChessPiece.PieceColor.Light : ChessPiece.PieceColor.Dark);
                        double newEvalOpponent = GetPiecesValue(lightTurn ? ChessPiece.PieceColor.Dark : ChessPiece.PieceColor.Light);
                        newEval = newEvalMy - newEvalOpponent;
                    }

                    // Add position to dictionary for memoization if the position is not
                    // yet in the dictionary or if the position is in the dictionary and is
                    // of lesser depth
                    if (!posInDict || (posInDict && depth < dictionaryDepth))
                    {
                        generatedPositions[boardPosition/*hashedPos*/] = depth;
                    }

                    // Update best move is newEval is better
                    if (newEval > bestMoveContext.scoreEval ||
                        /* RANDOMLY CHANGE IF SAME EVAL */
                        (newEval == bestMoveContext.scoreEval && r1.NextDouble() > 0.5)
                    )
                    {
                        bestMoveContext.scoreEval = newEval;
                        bestMoveContext.newLocation = pt;
                        bestMoveContext.piece = p;
                        if (depth == 0)
                        {
                            OnScoreImproved(this, bestMoveContext);
                        }
                    }

                    // Renew state
                    p.pieceType = pieceType;
                    playingField[p.Xindex, p.Yindex] = null;
                    p.Xindex = oldLocation.X;
                    p.Yindex = oldLocation.Y;
                    playingField[p.Xindex, p.Yindex] = p;
                    playingField[pt.X, pt.Y] = null;
                    if (taken != null)
                    {
                        playingField[pt.X, pt.Y] = taken;
                        if (taken.pieceColor == ChessPiece.PieceColor.Light)
                        {
                            piecesLight.AddLast(taken);
                        }
                        else if (taken.pieceColor == ChessPiece.PieceColor.Dark)
                        {
                            piecesDark.AddLast(taken);
                        }
                    }

                    //string cbInter3 = BoardToString();
                    //if (cbInter1.Equals(cbPre/*cbInter2*/) == false)
                    //{
                    //    int breakme = 0;
                    //}
                    if (depth % 2 == 0)
                    {
                        alpha = Math.Max(alpha, bestMoveContext.scoreEval);
                    }
                    else
                    {
                        beta = Math.Min(beta, bestMoveContext.scoreEval);
                    }

                    if (beta <= alpha /*&& depth > 0*/)
                    {
                        //canBreak = true;
                        //break;
                    }
                }
                if (canBreak && depth > 0)
                {
                    //break;
                }
                counter++;
            }

            lightTurn = savedTurnLight;
            //string cbPost = BoardToString();

            if (depth == 0)
            {
                if (bestMoveContext.newLocation.X != -1 && bestMoveContext.newLocation.Y != -1)
                {
                    OnScoreImproved(this, bestMoveContext);
                }
                else
                {
                    //bestMoveContext.scoreEval = depth % 2 == 0 ? 1000 : -1000;
                }
            }

            return bestMoveContext;
        }

        // Fourth iteration
        private /*double*/MiniMaxContext MiniMax4(int depth, int maxDepth, double alpha, double beta)
        {
            if (depth == 0)
            {

                generatedPositions = new Dictionary<string, int>();
                nodesCount = 0;
                movesCount = 0;
            }
            nodesCount++;
            LinkedList<ChessPiece> pieces = new LinkedList<ChessPiece>(); // lightTurn ? piecesLight : piecesDark;
            if (lightTurn)
            {
                foreach (ChessPiece p in piecesLight)
                {
                    pieces.AddLast(p);
                }
            }
            else
            {
                foreach (ChessPiece p in piecesDark)
                {
                    pieces.AddLast(p);
                }
            }
            LinkedList<Point> pieceMoves;
            MiniMaxContext bestMoveContext = new MiniMaxContext();
            bestMoveContext.piece = null;
            bestMoveContext.scoreEval = double.MinValue;//depth % 2 == 0 ? double.MinValue : double.MaxValue;
            bestMoveContext.newLocation = new Point(-1, -1);
            LinkedList<Point> allValid = GetAllValidMoves(lightTurn ? ChessPiece.PieceColor.Light : ChessPiece.PieceColor.Dark);
            if (allValid.Count == 0 && KingAttacked(!lightTurn ? ChessPiece.PieceColor.Light : ChessPiece.PieceColor.Dark))
            {
                bestMoveContext.scoreEval = -1000;//depth % 2 == 0 ? 1000 : -1000;
                return bestMoveContext;
            }
            bool savedTurnLight = lightTurn;

            //string cbPre = BoardToString();
            int counter = 0;
            bool canBreak = false;
            foreach (ChessPiece p in pieces)
            {
                ChessPiece.PieceType pieceType = p.pieceType;
                //string cbInter2 = BoardToString();
                pieceMoves = GetValidMoves(p);
                //string cbInter1 = BoardToString();

                //Console.WriteLine(cbInter1 + Environment.NewLine);

                foreach (Point pt in pieceMoves)
                {
                    movesCount++;
                    // save previous setup
                    Point oldLocation = new Point(p.Xindex, p.Yindex);
                    ChessPiece pieceAtNewLoc = playingField[pt.X, pt.Y];
                    ChessPiece taken = JustMove(p, pt.X, pt.Y);

                    //double newEvalMy = -1;
                    //double newEvalOpponent = -1;
                    //newEvalMy = GetPiecesValue(lightTurn ? ChessPiece.PieceColor.Light : ChessPiece.PieceColor.Dark);
                    //newEvalOpponent = GetPiecesValue(lightTurn ? ChessPiece.PieceColor.Dark : ChessPiece.PieceColor.Light);
                    //double newEval = -1;
                    //newEval = newEvalMy - newEvalOpponent;
                    //string boardPosition = BoardToString();

                    //double minimaxEval = 0;
                    //if (depth < maxDepth && generatedPositions.ContainsKey(boardPosition) == false)
                    //{
                    //    generatedPositions[boardPosition] = depth;
                    //    lightTurn = ! lightTurn;
                    //    MiniMaxContext recommendedMove = MiniMax1(depth + 1, maxDepth, alpha, beta);
                    //    //if ((recommendedMove.scoreEval > bestMoveContext.scoreEval && depth % 2 == 0) || (recommendedMove.scoreEval < bestMoveContext.scoreEval && depth % 2 == 1))
                    //    //{
                    //    //    bestMoveContext.scoreEval = recommendedMove.scoreEval;
                    //    //    if (depth == 0)
                    //    //    {
                    //    //        OnScoreImproved(this, bestMoveContext);
                    //    //    }
                    //    //}
                    //    minimaxEval = recommendedMove.scoreEval;
                    //}

                    //if ((newEval > bestMoveContext.scoreEval && depth % 2 == 0) || (newEval < bestMoveContext.scoreEval && depth % 2 == 1))
                    //{
                    //    bestMoveContext.scoreEval = newEval;
                    //    bestMoveContext.newLocation = pt;
                    //    bestMoveContext.piece = p;

                    //    if (depth == 0)
                    //    {
                    //        OnScoreImproved(this, bestMoveContext);
                    //    }
                    //}

                    string boardPosition = BoardToString();
                    //string hashedPos = hashSHA256(boardPosition, 16);
                    int dictionaryDepth = int.MaxValue;
                    bool posInDict = generatedPositions.TryGetValue(boardPosition/*hashedPos*/, out dictionaryDepth);
                    double newEval = -1;
                    double minimaxEval = double.MinValue;
                    // for d1
                    if (depth == 0)
                    {
                        double newEvalMy = newEvalMy = GetPiecesValue(lightTurn ? ChessPiece.PieceColor.Light : ChessPiece.PieceColor.Dark);
                        double newEvalOpponent = GetPiecesValue(lightTurn ? ChessPiece.PieceColor.Dark : ChessPiece.PieceColor.Light);
                        newEval = newEvalMy - newEvalOpponent;
                    }
                    if (depth < maxDepth)
                    {
                        if (posInDict && depth >= dictionaryDepth) // update anyway
                        {
                            if (depth == 0)
                            {
                                int breakme = 0;
                            }
                            double newEvalMy = newEvalMy = GetPiecesValue(lightTurn ? ChessPiece.PieceColor.Light : ChessPiece.PieceColor.Dark);
                            double newEvalOpponent = GetPiecesValue(lightTurn ? ChessPiece.PieceColor.Dark : ChessPiece.PieceColor.Light);
                            newEval = newEvalMy - newEvalOpponent;
                        }
                        else // try searching deeper
                        {
                            lightTurn = !lightTurn;

                            MiniMaxContext recommendedMove = MiniMax4(depth + 1, maxDepth, alpha, beta);

                            if (recommendedMove.newLocation.X == -1 || recommendedMove.newLocation.Y == -1)
                            {
                                double newEvalMy = newEvalMy = GetPiecesValue(lightTurn ? ChessPiece.PieceColor.Light : ChessPiece.PieceColor.Dark);
                                double newEvalOpponent = GetPiecesValue(lightTurn ? ChessPiece.PieceColor.Dark : ChessPiece.PieceColor.Light);
                                newEval = newEvalMy - newEvalOpponent;
                            }
                            else
                            {
                                minimaxEval = recommendedMove.scoreEval * -1;
                                newEval = minimaxEval;
                            }

                            lightTurn = !lightTurn;
                        }
                    }
                    else // is a leaf - set the move anyway
                    {
                        if (depth == 0)
                        {
                            int breakme = 0;
                        }
                        double newEvalMy = newEvalMy = GetPiecesValue(lightTurn ? ChessPiece.PieceColor.Light : ChessPiece.PieceColor.Dark);
                        double newEvalOpponent = GetPiecesValue(lightTurn ? ChessPiece.PieceColor.Dark : ChessPiece.PieceColor.Light);
                        newEval = newEvalMy - newEvalOpponent;
                    }

                    // Add position to dictionary for memoization if the position is not
                    // yet in the dictionary or if the position is in the dictionary and is
                    // of lesser depth
                    if (!posInDict || (posInDict && depth < dictionaryDepth))
                    {
                        generatedPositions[boardPosition/*hashedPos*/] = depth;
                    }

                    // Update best move is newEval is better
                    if (newEval > bestMoveContext.scoreEval ||
                        /* RANDOMLY CHANGE IF SAME EVAL */
                        (newEval == bestMoveContext.scoreEval && r1.NextDouble() > 0.5)
                    )
                    {
                        bestMoveContext.scoreEval = newEval;
                        bestMoveContext.newLocation = pt;
                        bestMoveContext.piece = p;
                        if (depth == 0)
                        {
                            OnScoreImproved(this, bestMoveContext);
                        }
                    }

                    // Renew state
                    p.pieceType = pieceType;
                    playingField[p.Xindex, p.Yindex] = null;
                    p.Xindex = oldLocation.X;
                    p.Yindex = oldLocation.Y;
                    playingField[p.Xindex, p.Yindex] = p;
                    playingField[pt.X, pt.Y] = null;
                    if (taken != null)
                    {
                        playingField[pt.X, pt.Y] = taken;
                        if (taken.pieceColor == ChessPiece.PieceColor.Light)
                        {
                            piecesLight.AddLast(taken);
                        }
                        else if (taken.pieceColor == ChessPiece.PieceColor.Dark)
                        {
                            piecesDark.AddLast(taken);
                        }
                    }

                    //string cbInter3 = BoardToString();
                    //if (cbInter1.Equals(cbPre/*cbInter2*/) == false)
                    //{
                    //    int breakme = 0;
                    //}
                    if (depth % 2 == 0)
                    {
                        alpha = Math.Max(alpha, bestMoveContext.scoreEval);
                    }
                    else
                    {
                        beta = Math.Min(beta, bestMoveContext.scoreEval);
                    }

                    if (beta <= alpha && depth > 0)
                    {
                        //canBreak = true;
                        //break;
                    }
                }
                if (canBreak && depth > 0)
                {
                    //break;
                }
                counter++;
            }

            lightTurn = savedTurnLight;
            //string cbPost = BoardToString();

            if (depth == 0)
            {
                if (bestMoveContext.newLocation.X != -1 && bestMoveContext.newLocation.Y != -1)
                {
                    OnScoreImproved(this, bestMoveContext);
                }
                else
                {
                    //bestMoveContext.scoreEval = depth % 2 == 0 ? 1000 : -1000;
                }
            }

            return bestMoveContext;
        }

        private /*double*/MiniMaxContext MiniMax5(int depth, int maxDepth, double alpha, double beta)
        {
            // Renew the public variables
            if (depth == 0)
            {

                generatedPositions = new Dictionary<string, int>();
                nodesCount = 0;
                movesCount = 0;
            }

            // Increase node count
            nodesCount++;

            // Copy the linkedList to avoid 'collection changed' error due to move simulation
            LinkedList<ChessPiece> pieces = new LinkedList<ChessPiece>(); // lightTurn ? piecesLight : piecesDark;
            if (lightTurn)
            {
                foreach (ChessPiece p in piecesLight)
                {
                    pieces.AddLast(p);
                }
            }
            else
            {
                foreach (ChessPiece p in piecesDark)
                {
                    pieces.AddLast(p);
                }
            }

            // Prepare local best move context
            MiniMaxContext bestMoveContext = new MiniMaxContext();
            bestMoveContext.piece = null;
            bestMoveContext.scoreEval = double.MinValue;/*depth % 2 == 0 ? double.MinValue : double.MaxValue;*/
            bestMoveContext.newLocation = new Point(-1, -1);

            // Generate all valid moves
            LinkedList<Point> allValid = GetAllValidMoves(lightTurn ? ChessPiece.PieceColor.Light : ChessPiece.PieceColor.Dark);

            // Check if player is in check mate
            //if (allValid.Count == 0 && KingAttacked(lightTurn ? ChessPiece.PieceColor.Light : ChessPiece.PieceColor.Dark))
            //{
            //    bestMoveContext.scoreEval = /*-1000;*/ depth % 2 == 1 ? 1000 : -1000;
            //    return bestMoveContext;
            //}

            // Save light/dark turn state
            bool savedTurnLight = lightTurn;
            int counter = 0;

            // Break occurs if alpha-beta condition is met
            bool canBreak = false;
            foreach (ChessPiece p in pieces)
            {
                // Save piece type in case of promotion simulation
                ChessPiece.PieceType pieceType = p.pieceType;
                // Get all valid piece moves
                LinkedList<Point> pieceMoves = GetValidMoves(p);

                // Iterate over each valid move
                foreach (Point pt in pieceMoves)
                {
                    // Increase number of simulated moves
                    movesCount++;

                    // Save state
                    Point oldLocation = new Point(p.Xindex, p.Yindex);
                    ChessPiece pieceAtNewLoc = playingField[pt.X, pt.Y];
                    ChessPiece taken = JustMove(p, pt.X, pt.Y);

                    // Generate board position as hashable string
                    string boardPosition = BoardToString();
                    int dictionaryDepth = int.MaxValue;
                    bool posInDict = generatedPositions.TryGetValue(boardPosition, out dictionaryDepth);
                    double newEval = double.MinValue;
                    double minimaxEval = double.MinValue;
                    // for d1
                    //if (depth == 0)
                    //{
                    //    double newEvalMy = newEvalMy = GetPiecesValue(lightTurn ? ChessPiece.PieceColor.Light : ChessPiece.PieceColor.Dark);
                    //    double newEvalOpponent = GetPiecesValue(!lightTurn ? ChessPiece.PieceColor.Light : ChessPiece.PieceColor.Dark);
                    //    newEval = newEvalMy - newEvalOpponent;
                    //}
                    if (depth < maxDepth)
                    {
                        if (posInDict && depth >= dictionaryDepth) // update anyway
                        {
                            double newEvalMy = newEvalMy = GetPiecesValue(lightTurn ? ChessPiece.PieceColor.Light : ChessPiece.PieceColor.Dark);
                            double newEvalOpponent = GetPiecesValue(lightTurn ? ChessPiece.PieceColor.Dark : ChessPiece.PieceColor.Light);
                            newEval = newEvalMy - newEvalOpponent;
                            //if (depth % 2 == 1)
                            //{
                            //    newEval = newEval * -1;
                            //}
                        }
                        else // try searching deeper
                        {
                            lightTurn = !lightTurn;

                            MiniMaxContext recommendedMove = MiniMax5(depth + 1, maxDepth, alpha, beta);
                            //recommendedMove.scoreEval = recommendedMove.scoreEval * -1;

                            if (recommendedMove.newLocation.X == -1 || recommendedMove.newLocation.Y == -1)
                            {
                                double newEvalMy = newEvalMy = GetPiecesValue(lightTurn ? ChessPiece.PieceColor.Light : ChessPiece.PieceColor.Dark);
                                double newEvalOpponent = GetPiecesValue(lightTurn ? ChessPiece.PieceColor.Dark : ChessPiece.PieceColor.Light);
                                newEval = newEvalMy - newEvalOpponent;
                                //if (depth % 2 == 1)
                                //{
                                //    newEval = newEval * -1;
                                //}
                            }
                            else
                            {
                                minimaxEval = recommendedMove.scoreEval * -1;
                                //if (depth % 2 == 1)
                                //{
                                //    minimaxEval *= -1;
                                //}
                                newEval = minimaxEval;
                            }

                            //if (depth % 2 == 0)
                            //{
                            //    alpha = Math.Max(alpha, minimaxEval);
                            //}
                            //else
                            //{
                            //    beta = Math.Min(beta, minimaxEval);
                            //}

                            lightTurn = !lightTurn;
                        }
                    }
                    else // is a leaf - set the move anyway
                    {
                        double newEvalMy = newEvalMy = GetPiecesValue(lightTurn ? ChessPiece.PieceColor.Light : ChessPiece.PieceColor.Dark);
                        double newEvalOpponent = GetPiecesValue(lightTurn ? ChessPiece.PieceColor.Dark : ChessPiece.PieceColor.Light);
                        newEval = newEvalMy - newEvalOpponent;
                        //if (depth % 2 == 1)
                        //{
                        //    newEval = newEval * -1;
                        //}
                    }

                    // Add position to dictionary for memoization if the position is not
                    // yet in the dictionary or if the position is in the dictionary and is
                    // of lesser depth
                    if (!posInDict || (posInDict && depth < dictionaryDepth))
                    {
                        generatedPositions[boardPosition/*hashedPos*/] = depth;
                    }

                    
                    // Update best move if newEval is better
                    if (/*(newEval > bestMoveContext.scoreEval && depth % 2 == 0) ||
                        (newEval < bestMoveContext.scoreEval && depth % 2 == 1) ||*/
                        newEval > bestMoveContext.scoreEval ||
                        /* RANDOMLY CHANGE IF SAME EVAL */
                        1 == 2
                        //(newEval == bestMoveContext.scoreEval && r1.NextDouble() > 0.5)
                    )
                    {
                        bestMoveContext.scoreEval = newEval;
                        bestMoveContext.newLocation = pt;
                        bestMoveContext.piece = p;
                        if (depth == 0)
                        {
                            OnScoreImproved(this, bestMoveContext);
                        }
                    }

                    // Renew state
                    p.pieceType = pieceType;
                    playingField[p.Xindex, p.Yindex] = null;
                    p.Xindex = oldLocation.X;
                    p.Yindex = oldLocation.Y;
                    playingField[p.Xindex, p.Yindex] = p;
                    playingField[pt.X, pt.Y] = null;
                    if (taken != null)
                    {
                        playingField[pt.X, pt.Y] = taken;
                        if (taken.pieceColor == ChessPiece.PieceColor.Light)
                        {
                            piecesLight.AddLast(taken);
                        }
                        else if (taken.pieceColor == ChessPiece.PieceColor.Dark)
                        {
                            piecesDark.AddLast(taken);
                        }
                    }

                    if (depth % 2 == 0)
                    {
                        alpha = Math.Max(alpha, bestMoveContext.scoreEval);
                    }
                    else
                    {
                        beta = Math.Min(beta, bestMoveContext.scoreEval);
                    }

                    if (alpha >= beta)
                    {
                        canBreak = true;
                        break;
                    }
                }
                if (canBreak)
                {
                    break;
                }
                counter++;
            }

            // Restore light/dark turn
            lightTurn = savedTurnLight;

            if (depth == 0)
            {
                // Report last (chosen) move
                if (bestMoveContext.newLocation.X != -1 && bestMoveContext.newLocation.Y != -1)
                {
                    OnScoreImproved(this, bestMoveContext);
                }
            }

            return bestMoveContext;
        }
    }
}