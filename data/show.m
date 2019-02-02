data = csvread('walk01.csv');
N = length(data);

x = data(1:(N/2));

w = cwt(x);
figure;
wscalogram('CWT', w);
