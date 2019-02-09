if(!settings.multipleView) settings.batchView=false;
settings.tex="pdflatex";
settings.inlinetex=true;
deletepreamble();
defaultfilename="itsasnap_source-1";
if(settings.render < 0) settings.render=4;
settings.outformat="";
settings.inlineimage=true;
settings.embed=true;
settings.toolbar=false;
viewportmargin=(2,2);


int factorial(int n) { // Tail recursion... why not?
if (n == 0 || n == 1)
return 1;
return n * factorial(n - 1);
}

void drawConnect(pair tloffset, int[] mapping = {0}, int cols = 3, real xd = 1, real yd = 1.5) {
int rows = mapping.length + 1;
for (int x = 0; x < cols; ++x) {
for (int y = 0; y < rows; ++y) {
if (y < rows - 1) {
int map = mapping[y];
int[] needs;
int[] truemap;

for (int c = 0; c < cols; ++c) needs.push(c);

for (int i = 0; i < cols; ++i) {
int fact = factorial(cols - i - 1);

int egg = map # fact; // Integer division lolololol
int indx = needs[egg];
needs.delete(egg);

map %= fact;

draw((tloffset + (i * xd, -y * yd)) -- (tloffset + (indx * xd, (-y-1) * yd)));
}
}

dot(tloffset + (x * xd, -y * yd));
}
}
}


size(70);

int[] ms = {2,5};

drawConnect((0, 0), ms);

draw(brace((-0.6, -3.2), (-0.6, 0.2), .3), black+1bp);
draw(brace((-0.2, 0.6), (2.2, 0.6), .3), black+1bp);

label("$n$", (-0.8, -1.5), W);
label("$3$", (1, 0.9), N);
