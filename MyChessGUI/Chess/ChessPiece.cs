using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace Chess
{
    public class ChessPiece
    {
        public int Xindex;
        public int Yindex;
        public PieceType pieceType;
        public PieceColor pieceColor;

        public ChessPiece()
        {
            baseInit();
        }

        public ChessPiece(int x, int y, PieceType pieceType, PieceColor pieceColor)
        {
            baseInit();
            this.Xindex = x;
            this.Yindex = y;
            this.pieceType = pieceType;
            this.pieceColor = pieceColor;
        }

        private void baseInit()
        {
            Xindex = -1;
            Yindex = -1;
        }

        public enum PieceType
        {
            Pawn,
            Knight,
            Bishop,
            Rook,
            Queen,
            King
        }

        public enum PieceColor
        {
            Light,
            Dark
        }

        public string ToString()
        {
            string rez = "";
            if(pieceType == PieceType.Pawn)
            {
                rez = "P";
            }
            else if (pieceType == PieceType.Bishop)
            {
                rez = "B";
            }
            else if (pieceType == PieceType.Knight)
            {
                rez = "N";
            }
            else if (pieceType == PieceType.Rook)
            {
                rez = "R";
            }
            else if (pieceType == PieceType.Queen)
            {
                rez = "Q";
            }
            else if (pieceType == PieceType.King)
            {
                rez = "K";
            }

            if(pieceColor == PieceColor.Dark)
            {
                rez = rez.ToLower();
            }

            return rez;
        }

        public double getPieceValue()
        {
            double val = 0;
            if (pieceType == PieceType.Pawn)
            {
                val = 1;
            }
            else if (pieceType == PieceType.Bishop)
            {
                val = 3;
            }
            else if (pieceType == PieceType.Knight)
            {
                val = 3;
            }
            else if (pieceType == PieceType.Rook)
            {
                val = 5;
            }
            else if (pieceType == PieceType.Queen)
            {
                val = 9;
            }
            else if (pieceType == PieceType.King)
            {
                val = /*1000*/0;
            }

            return val;
        }
    }
}
