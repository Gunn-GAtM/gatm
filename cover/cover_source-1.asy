if(!settings.multipleView) settings.batchView=false;
settings.tex="pdflatex";
settings.inlinetex=true;
deletepreamble();
defaultfilename="cover_source-1";
if(settings.render < 0) settings.render=4;
settings.outformat="";
settings.inlineimage=true;
settings.embed=true;
settings.toolbar=false;
viewportmargin=(2,2);

size(480);

pair cis(real theta) { // Gives points on the unit circle
return (cos(theta), sin(theta));
}


pair A = cis(-pi/6), B = cis(pi/2), C = cis(7*pi/6); // Starting triangle corners

for (int i = 0; i < 4; ++i) { // Draws the triangles and dots
draw(A--B--C--cycle);

dot(A);
dot(B);
dot(C);

if (i < 3) {
A *= -2; B *= -2; C *= -2; // Scales A,B,C to the next triangle
}
}

dot((0,0)); // Center dot

draw(A--(-1/2 * A), dashed);
draw(B--(-1/2 * B), dashed);
draw(C--(-1/2 * C), dashed);


label("{\bfseries \Huge{}A Geometric Approach to}", -1/2 * B, N);
draw(circle((0,0), 8));
label("{\bfseries \fontsize{60}{80} \selectfont{}Matrices}", 5/8 * B);

